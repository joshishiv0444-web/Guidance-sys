package com.example.aiorb

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.view.accessibility.AccessibilityManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.core.content.ContextCompat
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import kotlinx.coroutines.launch

enum class AppScreen { WELCOME, TUTORIAL, PERMISSIONS, DASHBOARD }

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { PremiumTheme { AppNavigator() } }
    }

    override fun onResume() {
        super.onResume()
        setContent { PremiumTheme { AppNavigator() } }
    }

    private fun hasOverlayPermission(): Boolean = Settings.canDrawOverlays(this)

    private fun hasAccessibilityPermission(): Boolean {
        val enabled = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
        return enabled?.contains("OrbAccessibilityService") == true
    }

    private fun hasAudioPermission(): Boolean {
        return ContextCompat.checkSelfPermission(this, android.Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
    }

    @Composable
    fun AppNavigator() {
        // Track lifecycle to re-evaluate the initial screen if permissions change in background
        val lifecycleOwner = LocalLifecycleOwner.current
        var forceRefresh by remember { mutableStateOf(0) }

        DisposableEffect(lifecycleOwner) {
            val observer = LifecycleEventObserver { _, event ->
                if (event == Lifecycle.Event.ON_RESUME) forceRefresh++
            }
            lifecycleOwner.lifecycle.addObserver(observer)
            onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
        }

        var currentScreen by remember(forceRefresh) {
            mutableStateOf(
                when {
                    hasOverlayPermission() && hasAccessibilityPermission() && hasAudioPermission() && SharedPrefsHelper.isOnboardingComplete(this) -> AppScreen.DASHBOARD
                    !SharedPrefsHelper.isOnboardingComplete(this) -> AppScreen.WELCOME
                    else -> AppScreen.PERMISSIONS
                }
            )
        }

        // Animated screen transitions
        Crossfade(targetState = currentScreen, animationSpec = androidx.compose.animation.core.tween(500),
            label = ""
        ) { screen ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Brush.verticalGradient(listOf(Color(0xFF0A0A0A), Color(0xFF1A1A2E))))
            ) {
                when (screen) {
                    AppScreen.WELCOME -> WelcomeScreen(onNext = { currentScreen = AppScreen.TUTORIAL })
                    AppScreen.TUTORIAL -> TutorialScreen(onNext = { currentScreen = AppScreen.PERMISSIONS })
                    AppScreen.PERMISSIONS -> PermissionsScreen(
                        onNext = {
                            SharedPrefsHelper.setOnboardingComplete(this@MainActivity, true)
                            currentScreen = AppScreen.DASHBOARD
                        }
                    )
                    AppScreen.DASHBOARD -> MainDashboard(
                        onCheckPermissions = {
                            if (!hasOverlayPermission() || !hasAccessibilityPermission()) {
                                currentScreen = AppScreen.PERMISSIONS
                            }
                        }
                    )
                }
            }
        }
    }

    @Composable
    fun PremiumTheme(content: @Composable () -> Unit) {
        MaterialTheme(
            colorScheme = darkColorScheme(
                primary   = Color(0xFF00C2FF),
                secondary = Color(0xFF00FF94),
                background = Color(0xFF0A0A0A),
                surface   = Color(0xFF1E1E1E),
                error     = Color(0xFFFF3D00)
            ),
            content = content
        )
    }

    // ─── Screen 1: Welcome ─────────────────────────────────────────────────────
    @Composable
    fun WelcomeScreen(onNext: () -> Unit) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .background(
                        Brush.radialGradient(listOf(Color(0xFF00C2FF).copy(alpha = 0.5f), Color.Transparent)),
                        CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Default.Lock, contentDescription = null, tint = Color(0xFF00C2FF), modifier = Modifier.size(64.dp))
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            Text("Meet SafeAssist", fontSize = 32.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                "Your personal, AI-powered screen guardian. We monitor for scams, suspicious links, and payment hesitation so you can browse safely.",
                fontSize = 16.sp, color = Color.Gray, textAlign = TextAlign.Center, lineHeight = 24.sp
            )
            Spacer(modifier = Modifier.height(48.dp))
            Button(
                onClick = onNext,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00C2FF))
            ) {
                Text("Get Started", color = Color.Black, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
        }
    }

    // ─── Screen 2: Tutorial ────────────────────────────────────────────────────
    @Composable
    fun TutorialScreen(onNext: () -> Unit) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(40.dp))
            Text("How it Works", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(modifier = Modifier.height(8.dp))
            Text("Three ways the Orb protects you:", fontSize = 16.sp, color = Color.Gray)
            Spacer(modifier = Modifier.height(32.dp))

            TutorialItem(
                icon = "👆", color = Color(0xFF00C2FF), title = "Tap for Help",
                desc = "Tap the floating orb anytime. It scans your screen and asks the AI what you should do next."
            )
            Spacer(modifier = Modifier.height(24.dp))
            TutorialItem(
                icon = "🔗", color = Color(0xFF0088FF), title = "Link Detection",
                desc = "If a suspicious URL appears on screen, the orb pulses Blue and automatically reports it."
            )
            Spacer(modifier = Modifier.height(24.dp))
            TutorialItem(
                icon = "💳", color = Color(0xFFFF6D00), title = "Payment Guard",
                desc = "Stuck on a payment app? The orb glows Orange after 15s, and auto-reports to AI after 25s."
            )

            Spacer(modifier = Modifier.height(48.dp))
            Button(
                onClick = onNext,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00C2FF))
            ) {
                Text("Next: Setup", color = Color.Black, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(32.dp))
        }
    }

    @Composable
    fun TutorialItem(icon: String, color: Color, title: String, desc: String) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
            shape = RoundedCornerShape(20.dp)
        ) {
            Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier.size(56.dp).background(color.copy(alpha = 0.15f), RoundedCornerShape(16.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(icon, fontSize = 24.sp)
                }
                Spacer(Modifier.width(16.dp))
                Column {
                    Text(title, fontWeight = FontWeight.Bold, color = Color.White, fontSize = 18.sp)
                    Spacer(Modifier.height(4.dp))
                    Text(desc, fontSize = 13.sp, color = Color.Gray, lineHeight = 18.sp)
                }
            }
        }
    }

    // ─── Screen 3: Permissions ─────────────────────────────────────────────────
    @Composable
    fun PermissionsScreen(onNext: () -> Unit) {
        val lifecycleOwner = LocalLifecycleOwner.current
        val context = LocalContext.current
        var overlayGranted by remember { mutableStateOf(hasOverlayPermission()) }
        var accGranted by remember { mutableStateOf(hasAccessibilityPermission()) }
        var audioGranted by remember { mutableStateOf(hasAudioPermission()) }

        // Launcher for Audio Permission
        val audioLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
            androidx.activity.result.contract.ActivityResultContracts.RequestPermission()
        ) { isGranted: Boolean ->
            audioGranted = isGranted
        }

        DisposableEffect(lifecycleOwner) {
            val observer = LifecycleEventObserver { _, event ->
                if (event == Lifecycle.Event.ON_RESUME) {
                    overlayGranted = hasOverlayPermission()
                    accGranted = hasAccessibilityPermission()
                    audioGranted = hasAudioPermission()
                }
            }
            lifecycleOwner.lifecycle.addObserver(observer)
            onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
        }

        val allGranted = overlayGranted && accGranted && audioGranted

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Spacer(modifier = Modifier.height(40.dp))
            Text("Enable Security Engine", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(modifier = Modifier.height(8.dp))
            Text("We need two permissions to protect you across all your apps.", fontSize = 16.sp, color = Color.Gray)
            Spacer(modifier = Modifier.height(16.dp))

            PermissionCard(
                title = "Microphone Access",
                subtitle = "Required to speak to the AI and explain your problem out loud.",
                icon = Icons.Default.Phone,
                granted = audioGranted,
                onClick = {
                    if (!audioGranted) {
                        audioLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
                    }
                }
            )

            Spacer(modifier = Modifier.height(32.dp))

            PermissionCard(
                title = "1. Display Over Other Apps",
                subtitle = "Allows the floating AI Orb to stay visible on your screen so you can tap it anytime.",
                granted = overlayGranted,
                icon = Icons.Default.List
            ) {
                startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
            }

            Spacer(Modifier.height(24.dp))

            PermissionCard(
                title = "2. Accessibility Service",
                subtitle = "Allows the engine to read the text on your screen privately to detect scams and links.",
                granted = accGranted,
                icon = Icons.Default.Search
            ) {
                startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            }

            Spacer(modifier = Modifier.height(48.dp))
            
            Button(
                onClick = onNext,
                enabled = allGranted,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (allGranted) Color(0xFF00FF94) else Color(0xFF2E2E2E),
                    disabledContainerColor = Color(0xFF2E2E2E)
                )
            ) {
                Text(
                    if (allGranted) "Complete Setup" else "Grant permissions to continue",
                    color = if (allGranted) Color.Black else Color.Gray,
                    fontSize = 18.sp, fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.height(32.dp))
        }
    }

    @Composable
    fun PermissionCard(title: String, subtitle: String, granted: Boolean, icon: ImageVector, onClick: () -> Unit) {
        Card(
            modifier = Modifier.fillMaxWidth().clickable { onClick() },
            colors = CardDefaults.cardColors(containerColor = if (granted) Color(0xFF1E2E1E) else Color(0xFF1E1E1E)),
            shape = RoundedCornerShape(20.dp)
        ) {
            Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    if (granted) Icons.Default.CheckCircle else icon,
                    contentDescription = null,
                    tint = if (granted) Color(0xFF00FF94) else Color(0xFF00C2FF),
                    modifier = Modifier.size(32.dp)
                )
                Spacer(Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(Modifier.height(4.dp))
                    Text(subtitle, fontSize = 13.sp, color = Color.Gray, lineHeight = 18.sp)
                }
            }
        }
    }

    // ─── Screen 4: Main Dashboard ──────────────────────────────────────────────
    @Composable
    fun MainDashboard(onCheckPermissions: () -> Unit) {
        // Double check permissions every time we render the dashboard
        LaunchedEffect(Unit) { onCheckPermissions() }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.Start
        ) {
            Spacer(modifier = Modifier.height(24.dp))
            Text("SafeAssist", fontSize = 34.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Text("AI-Powered Screen Guardian", fontSize = 14.sp, color = Color.Gray)
            
            Spacer(Modifier.height(32.dp))
            StatusCard()
            
            Spacer(Modifier.height(32.dp))
            Text("Quick Settings", fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
            Spacer(Modifier.height(16.dp))
            
            // Re-use the tutorial items for a nice visual dashboard layout
            TutorialItem(
                icon = "🛡️", color = Color(0xFF00FF94), title = "Engine Active",
                desc = "Accessibility scanner is running quietly in the background."
            )
            Spacer(Modifier.height(16.dp))
            TutorialItem(
                icon = "⏳", color = Color(0xFFFFD600), title = "Payment Guard Active",
                desc = "Warning at 15s. Auto-report at 25s."
            )
            
            Spacer(Modifier.height(32.dp))
            Text("AI Language Preference", fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
            Spacer(Modifier.height(16.dp))
            
            val context = LocalContext.current
            var isHindi by remember { mutableStateOf(SharedPrefsHelper.isHindiLanguage(context)) }
            
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
                shape = RoundedCornerShape(20.dp)
            ) {
                Row(
                    modifier = Modifier.padding(20.dp).fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(if (isHindi) "Hindi / Hinglish" else "English (US)", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        Spacer(Modifier.height(4.dp))
                        Text(if (isHindi) "Voice and AI will respond in Hindi." else "Voice and AI will respond in English.", fontSize = 13.sp, color = Color.Gray, lineHeight = 18.sp)
                    }
                    Switch(
                        checked = isHindi,
                        onCheckedChange = { checked ->
                            isHindi = checked
                            SharedPrefsHelper.setHindiLanguage(context, checked)
                            OrbAccessibilityService.instance?.updateVoiceLanguage(checked)
                        },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = Color.White,
                            checkedTrackColor = Color(0xFF00FF94),
                            uncheckedThumbColor = Color.White,
                            uncheckedTrackColor = Color.Gray
                        )
                    )
                }
            }

            Spacer(Modifier.height(32.dp))
            AppInsightsCard()

            Spacer(Modifier.height(48.dp))
            Button(
                onClick = {
                    startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
                },
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E2E2E))
            ) {
                Text("Manage Android Settings", color = Color.White, fontSize = 16.sp)
            }
        }
    }

    @Composable
    fun StatusCard() {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
            shape = RoundedCornerShape(20.dp)
        ) {
            Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .background(Color(0xFF00FF94).copy(alpha = 0.15f), RoundedCornerShape(16.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Default.CheckCircle, contentDescription = null, tint = Color(0xFF00FF94), modifier = Modifier.size(32.dp))
                }
                Spacer(Modifier.width(16.dp))
                Column {
                    Text("System Protected", fontWeight = FontWeight.Bold, color = Color.White, fontSize = 18.sp)
                    Spacer(Modifier.height(4.dp))
                    Text("The AI Orb is currently active and monitoring for threats.", fontSize = 13.sp, color = Color.Gray, lineHeight = 18.sp)
                }
            }
        }
    }

    @Composable
    fun AppInsightsCard() {
        val context = LocalContext.current
        var struggleApps by remember { mutableStateOf(listOf<com.example.aiorb.models.AppTelemetry>()) }
        var trustedApps by remember { mutableStateOf(listOf<com.example.aiorb.models.AppTelemetry>()) }
        var isSyncing by remember { mutableStateOf(false) }
        val coroutineScope = rememberCoroutineScope()

        // Fetch telemetry stats when dashboard is loaded
        LaunchedEffect(Unit) {
            struggleApps = TelemetryManager.getTopStruggleApps(context, 3)
            trustedApps = TelemetryManager.getTopTrustedApps(context, 3)
        }

        Column(modifier = Modifier.fillMaxWidth()) {
            Text("UX Analytics (B2B Telemetry)", fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
            Spacer(Modifier.height(16.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
                shape = RoundedCornerShape(20.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp).fillMaxWidth()) {
                    Text("Top Struggle Areas", color = Color(0xFFFF3D00), fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(Modifier.height(8.dp))
                    if (struggleApps.isEmpty()) {
                        Text("Not enough data yet.", fontSize = 14.sp, color = Color.Gray)
                    } else {
                        struggleApps.forEach { app ->
                            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(app.packageName.substringAfterLast('.'), color = Color.White, fontSize = 14.sp, maxLines = 1, modifier = Modifier.weight(1f))
                                Text("${app.helpRequestCount} help requests", color = Color.Gray, fontSize = 12.sp)
                            }
                        }
                    }

                    Spacer(Modifier.height(24.dp))

                    Text("Highly Trusted Apps", color = Color(0xFF00FF94), fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(Modifier.height(8.dp))
                    if (trustedApps.isEmpty()) {
                        Text("Not enough data yet.", fontSize = 14.sp, color = Color.Gray)
                    } else {
                        trustedApps.forEach { app ->
                            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(app.packageName.substringAfterLast('.'), color = Color.White, fontSize = 14.sp, maxLines = 1, modifier = Modifier.weight(1f))
                                Text(app.displayRating, color = Color.Gray, fontSize = 12.sp)
                            }
                        }
                    }

                    Spacer(Modifier.height(24.dp))
                    Button(
                        onClick = {
                            isSyncing = true
                            coroutineScope.launch {
                                try {
                                    val allStats = TelemetryManager.getAllStatsRaw(context)
                                    val payload = allStats.map {
                                        com.example.aiorb.models.FrictionPayload(
                                            app = it.packageName,
                                            screen = "Overall",
                                            avgHesitation = it.helpRequestCount,
                                            oscillationRate = it.openCount
                                        )
                                    }
                                    val response = com.example.aiorb.network.RetrofitClient.instance.syncTelemetry(payload)
                                    if (response.isSuccessful) {
                                        android.widget.Toast.makeText(context, "Data Synced to MongoDB!", android.widget.Toast.LENGTH_SHORT).show()
                                    } else {
                                        android.widget.Toast.makeText(context, "Sync Failed", android.widget.Toast.LENGTH_SHORT).show()
                                    }
                                } catch (e: Exception) {
                                    android.widget.Toast.makeText(context, "Error: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                                } finally {
                                    isSyncing = false
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00C2FF)),
                        enabled = !isSyncing
                    ) {
                        Text(if (isSyncing) "Syncing..." else "Sync Data to MongoDB Cloud", color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
