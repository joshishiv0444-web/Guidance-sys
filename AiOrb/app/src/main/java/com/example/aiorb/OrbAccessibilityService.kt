package com.example.aiorb

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.graphics.Rect
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.example.aiorb.models.*
import com.example.aiorb.network.RetrofitClient
import com.google.gson.Gson
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.UUID
import java.util.regex.Pattern

class OrbAccessibilityService : AccessibilityService() {

    companion object {
        var instance: OrbAccessibilityService? = null

        // Matches http/https URLs and bare domains like "example.com/path"
        private val URL_PATTERN: Pattern = Pattern.compile(
            "(https?://[\\w\\-._~:/?#\\[\\]@!$&'()*+,;=%]+)" +
            "|(www\\.([\\w\\-]+\\.)+[\\w\\-]+([/?#][\\S]*)?)" +
            "|(([\\w\\-]+\\.)(com|net|org|in|io|co|gov|edu|info|biz|app|xyz)([/?#][\\S]*)?)",
            Pattern.CASE_INSENSITIVE
        )
    }

    private val handler = Handler(Looper.getMainLooper())
    private val serviceScope = CoroutineScope(Dispatchers.IO)
    private val sessionId = "session-${UUID.randomUUID().toString().take(8)}"

    private var currentPackageName = ""
    private var currentScreenDescription = "Unknown screen"
    private var isPaymentScreen = false
    private var voiceManager: VoiceManager? = null

    // ─── Two-Stage Payment Hesitation Timers ─────────────────────────────────
    private val STAGE_1_MS = 15_000L // 15s → glow orange
    private val STAGE_2_MS = 25_000L // 25s → report to AI
    private var stage1Fired = false   // Track if stage 1 is active

    // Payment content keywords — works even on emulator without real payment apps
    private val PAYMENT_CONTENT_KEYWORDS = listOf(
        "pay", "upi", "bank", "ifsc", "amount", "transfer",
        "beneficiary", "account number", "send money", "wallet",
        "checkout", "card number", "cvv", "expiry"
    )

    // Stage 1: Glow orange — visual warning only, no report yet
    private val stage1Runnable = Runnable {
        if (!isPaymentScreen) return@Runnable
        stage1Fired = true
        Log.d("SafeAssist", "Stage 1 (15s): Glowing orange — user might be stuck")
        OrbState.orbColor.value = OrbState.COLOR_WARNING
        OrbState.message.value = "Stuck? Tap the orb for help 💡"
        // Schedule Stage 2 (10 more seconds)
        handler.postDelayed(stage2Runnable, STAGE_2_MS - STAGE_1_MS)
    }

    // Stage 2: Still stuck after 25s → NOW send report
    private val stage2Runnable = Runnable {
        if (!isPaymentScreen) return@Runnable
        stage1Fired = false
        Log.d("SafeAssist", "Stage 2 (25s): User still stuck — sending report to AI")
        OrbState.orbColor.value = OrbState.COLOR_HESITATION
        OrbState.message.value = "Analyzing payment screen..."
        captureAndSendReport("I have been stuck on this payment screen for a while")
    }

    // Debounce link detection — avoid spamming reports for the same link
    private var lastDetectedLink = ""
    private var lastLinkReportTime = 0L
    private val LINK_DEBOUNCE_MS = 10_000L // 10 seconds

    private val PAYMENT_APPS = listOf(
        "com.google.android.apps.nbu.paisa.user",
        "com.phonepe.app",
        "net.one97.paytm",
        "in.amazon.mShop.android.shopping",
        "com.mobikwik_new",
        "com.freecharge.android"
    )



    // ─── Lifecycle ────────────────────────────────────────────────────────────
    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        val isHindi = SharedPrefsHelper.isHindiLanguage(this)
        voiceManager = VoiceManager(this, isHindi)
        Log.d("SafeAssist", "Sensory Layer Connected | Session: $sessionId")
        startForegroundService(Intent(this, FloatingOrbService::class.java))
    }

    fun updateVoiceLanguage(isHindi: Boolean) {
        voiceManager?.setLanguage(isHindi)
    }

    override fun onUnbind(intent: Intent?): Boolean {
        instance = null
        voiceManager?.destroy()
        stopService(Intent(this, FloatingOrbService::class.java))
        return super.onUnbind(intent)
    }

    override fun onInterrupt() {
        instance = null
    }

    // ─── Main Event Handler ───────────────────────────────────────────────────
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        event.packageName?.toString()?.let { pkg ->
            if (pkg != currentPackageName) {
                currentPackageName = pkg
                TelemetryManager.trackAppOpen(this, pkg)
            }
            // Set payment screen from package name first
            isPaymentScreen = PAYMENT_APPS.contains(pkg)
        }

        when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                // 1. ALWAYS reset timers on new window, even if it's a secure screen (GPay)
                stage1Fired = false
                resetHesitationTimer()
                if (!stage1Fired) clearWarning()

                // 2. ATTEMPT to scrape screen content (will fail gracefully on FLAG_SECURE apps)
                val source = event.source ?: rootInActiveWindow
                if (source != null) {
                    val elements = mutableListOf<UIElement>()
                    scrapeUI(source, elements)
                    source.recycle()

                    val screenType = classifyScreen(elements)
                    currentScreenDescription = buildScreenDescription(screenType, elements)

                    // Fallback: Also detect payment screen from screen content keywords
                    val allText = elements.joinToString(" ") { it.text }.lowercase()
                    if (!isPaymentScreen) {
                        val isLauncher = currentPackageName.contains("launcher", ignoreCase = true) || 
                                         currentPackageName.contains("home", ignoreCase = true) ||
                                         currentPackageName.contains("systemui", ignoreCase = true)
                        
                        if (!isLauncher) {
                            isPaymentScreen = PAYMENT_CONTENT_KEYWORDS.count { allText.contains(it) } >= 2
                            // If it just became a payment screen via content, start timer now
                            if (isPaymentScreen) resetHesitationTimer()
                        }
                    }

                    detectAndReportLinks(allText, elements, screenType)
                    autoSendScreenMetadata(screenType, elements)
                }
            }

            AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED -> {
                // 1. Restart timer on dynamic content changes if we are on a payment screen
                if (!stage1Fired && isPaymentScreen) {
                    resetHesitationTimer()
                }

                // 2. ATTEMPT to scrape for new links/content
                val source = event.source ?: rootInActiveWindow
                if (source != null) {
                    val elements = mutableListOf<UIElement>()
                    scrapeUI(source, elements)
                    source.recycle()

                    val screenType = classifyScreen(elements)
                    currentScreenDescription = buildScreenDescription(screenType, elements)

                    val allText = elements.joinToString(" ") { it.text }.lowercase()
                    if (!isPaymentScreen) {
                        val isLauncher = currentPackageName.contains("launcher", ignoreCase = true) || 
                                         currentPackageName.contains("home", ignoreCase = true) ||
                                         currentPackageName.contains("systemui", ignoreCase = true)
                        if (!isLauncher) {
                            isPaymentScreen = PAYMENT_CONTENT_KEYWORDS.count { allText.contains(it) } >= 2
                            if (isPaymentScreen && !stage1Fired) resetHesitationTimer()
                        }
                    }

                    detectAndReportLinks(allText, elements, screenType)
                }
            }

            AccessibilityEvent.TYPE_VIEW_CLICKED -> {
                // User clicked — they are not stuck, cancel both timers
                stage1Fired = false
                handler.removeCallbacks(stage1Runnable)
                handler.removeCallbacks(stage2Runnable)
                
                // Only reset colour if it was a payment warning
                if (OrbState.orbColor.value == OrbState.COLOR_WARNING ||
                    OrbState.orbColor.value == OrbState.COLOR_HESITATION) {
                    OrbState.orbColor.value = OrbState.COLOR_NORMAL
                    OrbState.message.value = ""
                }
                
                // Restart timers fresh after the click
                resetHesitationTimer()
            }
        }
    }

    // ─── Link Detection ───────────────────────────────────────────────────────
    private fun detectAndReportLinks(fullText: String, elements: List<UIElement>, screenType: String) {
        val matcher = URL_PATTERN.matcher(fullText)
        if (!matcher.find()) return // No link on screen — do nothing

        val detectedLink = matcher.group().trim()
        val now = System.currentTimeMillis()

        // Debounce: don't re-report the same link within 10 seconds
        if (detectedLink == lastDetectedLink && (now - lastLinkReportTime) < LINK_DEBOUNCE_MS) return

        lastDetectedLink = detectedLink
        lastLinkReportTime = now

        Log.d("SafeAssist", "Link detected on screen: $detectedLink")

        // Flash the orb orange-red to signal a link was found
        handler.post {
            OrbState.orbColor.value = OrbState.COLOR_SENDING
            OrbState.message.value = "🔗 Link detected — analyzing..."
        }

        serviceScope.launch {
            try {
                val req = URLRequest(url = detectedLink)
                val response = RetrofitClient.instance.checkUrl(req)

                handler.post {
                    if (response.isSuccessful) {
                        val body = response.body()
                        if (body != null && body.urlReputation.contains("malicious", ignoreCase = true)) {
                            OrbState.orbColor.value = OrbState.COLOR_HESITATION // Gold/Warning
                            OrbState.message.value = "⚠️ Warning: Suspicious Link!"
                        } else {
                            OrbState.orbColor.value = OrbState.COLOR_NORMAL
                            OrbState.message.value = "✓ Link appears safe"
                            // Clear message shortly
                            handler.postDelayed({ OrbState.message.value = "" }, 2500)
                        }
                    } else {
                        OrbState.orbColor.value = OrbState.COLOR_NORMAL
                        OrbState.message.value = ""
                    }
                }
            } catch (e: Exception) {
                Log.e("SafeAssist", "Link check error: ${e.message}")
                handler.post {
                    OrbState.orbColor.value = OrbState.COLOR_NORMAL
                    OrbState.message.value = ""
                }
            }
        }
    }

    // ─── Public: Called when user TAPS or LONG PRESSES the orb ────────────────
    fun handleOrbSingleTap() {
        if (OrbState.isListening.value) return
        TelemetryManager.trackHelpRequest(this, currentPackageName)
        captureAndSendReport("What should I do here?")
    }

    fun handleOrbLongPress() {
        if (OrbState.isListening.value) return
        TelemetryManager.trackHelpRequest(this, currentPackageName)

        handler.post {
            OrbState.orbColor.value = OrbState.COLOR_LISTENING
            OrbState.message.value = "Listening..."
        }

        voiceManager?.startListening { spokenText ->
            val query = if (!spokenText.isNullOrBlank()) spokenText else "What should I do here?"
            captureAndSendReport(query)
        }
    }

    fun stopVoice() {
        voiceManager?.stopSpeaking()
    }

    fun captureAndSendReport(userQuery: String = "What should I do here?") {
        serviceScope.launch {
            try {
                handler.post {
                    OrbState.orbColor.value = OrbState.COLOR_THINKING
                    OrbState.message.value = "Thinking..."
                }

                val root = rootInActiveWindow
                val elements = mutableListOf<UIElement>()
                if (root != null) {
                    scrapeUI(root, elements)
                    root.recycle()
                }

                val screenType = classifyScreen(elements)
                val elementLabels = elements.map { it.toLabel() }.filter { it.isNotBlank() }.distinct()

                // Check if there's a link in the current screen text
                val allText = elements.joinToString(" ") { it.text }
                val matcher = URL_PATTERN.matcher(allText)
                val linkFound = if (matcher.find()) matcher.group().trim() else null
                val riskLevel = if (linkFound != null || isPaymentScreen) "MEDIUM" else "LOW"

                var finalQuery = if (linkFound != null) "Link on screen: $linkFound. $userQuery" else userQuery
                if (SharedPrefsHelper.isHindiLanguage(this@OrbAccessibilityService)) {
                    finalQuery += " (Please reply in Hindi/Hinglish)"
                }

                // Use ElementMappingContext for better structured backend parsing
                val screenCtx = ElementMappingContext(
                    screen = screenType,
                    elements = elementLabels.take(15)
                )

                val req = GuidanceRequest(
                    sessionId = sessionId,
                    userQuery = finalQuery,
                    screenContext = screenCtx,
                    riskLevel = riskLevel
                )

                Log.d("SafeAssist", "Sending GuidanceRequest: ${Gson().toJson(req)}")
                val response = RetrofitClient.instance.getGuidance(req)

                handler.post {
                    if (response.isSuccessful && response.body() != null) {
                        val body = response.body()!!
                        
                        if (body.hardStop || body.fraudRisk == "HIGH") {
                            OrbState.orbColor.value = OrbState.COLOR_WARNING // High Alert Color
                        } else {
                            OrbState.orbColor.value = OrbState.COLOR_NORMAL
                        }
                        
                        OrbState.message.value = body.output
                        
                        // Speak the voice output
                        voiceManager?.speak(body.voiceOutput)

                    } else {
                        OrbState.message.value = "Error connecting to AI backend."
                        OrbState.orbColor.value = OrbState.COLOR_NORMAL
                        handler.postDelayed({ OrbState.message.value = "" }, 3000)
                    }
                }

            } catch (e: Exception) {
                Log.e("SafeAssist", "Capture error: ${e.message}")
                handler.post {
                    OrbState.orbColor.value = OrbState.COLOR_NORMAL
                    OrbState.message.value = "Network error. Server asleep?"
                    handler.postDelayed({ OrbState.message.value = "" }, 3000)
                }
            }
        }
    }

    // ─── Auto Screen Metadata ─────────────────────────────────────────────────
    private fun autoSendScreenMetadata(screenType: String, elements: List<UIElement>) {
        serviceScope.launch {
            try {
                val labels = elements.map { it.toLabel() }.filter { it.isNotBlank() }.distinct().take(15)
                val screenCtx = ElementMappingContext(
                    screen = screenType,
                    elements = labels
                )

                val req = ScamRequest(screenContext = screenCtx)
                val response = RetrofitClient.instance.checkScam(req)

                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    Log.d("SafeAssist", "Scam Check: Label=${body.label}, Risk=${body.riskLevel}, Prob=${body.modelProb}")

                    if (body.riskLevel == "HIGH" || body.label == "scam") {
                        handler.post {
                            OrbState.orbColor.value = OrbState.COLOR_WARNING
                            OrbState.message.value = "⚠️ High Risk Screen Detected"
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("SafeAssist", "Auto Scam Check Error: ${e.message}")
            }
        }
    }

    // ─── Recursive UI Scraper ─────────────────────────────────────────────────
    private fun scrapeUI(node: AccessibilityNodeInfo, out: MutableList<UIElement>, depth: Int = 0) {
        if (depth > 50) return
        val className = node.className?.toString() ?: ""
        val isInput = node.isEditable || className.contains("EditText")
        val isButton = node.isClickable && (className.contains("Button") || className.contains("ImageButton"))
        val text = node.text?.toString() ?: node.contentDescription?.toString() ?: ""

        if (text.isNotBlank() || isInput || isButton) {
            val rect = Rect()
            node.getBoundsInScreen(rect)
            out.add(UIElement(
                type = when { isInput -> "input"; isButton -> "button"; else -> "text" },
                id = node.viewIdResourceName ?: "unknown",
                text = text,
                isClickable = node.isClickable,
                isEditable = node.isEditable,
                bounds = "[${rect.left},${rect.top}][${rect.right},${rect.bottom}]"
            ))
        }

        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                scrapeUI(child, out, depth + 1)
                child.recycle()
            }
        }
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────
    private fun classifyScreen(elements: List<UIElement>): String {
        val labels = elements.joinToString(" ") { it.text }.lowercase()
        return when {
            isPaymentScreen                                          -> "payment_page"
            labels.contains("ifsc") || labels.contains("account number") -> "bank_transfer_page"
            labels.contains("password") && labels.contains("login")  -> "login_page"
            labels.contains("otp") && labels.contains("submit")      -> "otp_verification_page"
            else                                                     -> "general_page"
        }
    }

    private fun buildScreenDescription(screenType: String, elements: List<UIElement>): String {
        val inputs = elements.filter { it.isEditable }.map { it.text.ifBlank { "input field" } }
        return when (screenType) {
            "payment_page"          -> "Payment screen with ${inputs.joinToString(", ").ifBlank { "input fields" }}"
            "bank_transfer_page"    -> "Bank transfer screen, add beneficiary"
            "login_page"            -> "Login screen with credentials"
            "otp_verification_page" -> "OTP verification screen"
            else                    -> "Screen with ${elements.size} elements"
        }
    }

    private fun resetHesitationTimer() {
        handler.removeCallbacks(stage1Runnable)
        handler.removeCallbacks(stage2Runnable)
        if (isPaymentScreen) {
            handler.postDelayed(stage1Runnable, STAGE_1_MS)
        }
    }

    private fun clearWarning() {
        if (OrbState.orbColor.value != OrbState.COLOR_SENDING) {
            OrbState.orbColor.value = OrbState.COLOR_NORMAL
            // We don't wipe the message instantly if they just received a guidance response
        }
    }
}
