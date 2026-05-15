package com.example.aiorb

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.WindowManager
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.*
import androidx.savedstate.*

object OrbState {
    val COLOR_NORMAL     = Color(0xFF00C2FF) // Electric Blue
    val COLOR_SENDING    = Color(0xFF0088FF) // Deep Blue (Sending Data)
    val COLOR_LISTENING  = Color(0xFF00FF94) // Spring Green
    val COLOR_HESITATION = Color(0xFFFFD600) // Golden Yellow
    val COLOR_WARNING    = Color(0xFFFF6D00) // Bright Orange (15s payment warning)
    val COLOR_DANGER     = Color(0xFFFF3D00) // Vivid Red
    val COLOR_THINKING   = Color(0xFFB142FF) // Deep Glowing Purple

    val orbColor  = mutableStateOf(COLOR_NORMAL)
    val message   = mutableStateOf("")
    val isListening = mutableStateOf(false)
    val isSpeaking  = mutableStateOf(false)
}

class FloatingOrbService : Service(), LifecycleOwner, ViewModelStoreOwner, SavedStateRegistryOwner {

    private lateinit var windowManager: WindowManager
    private var composeView: ComposeView? = null
    private var layoutParams: WindowManager.LayoutParams? = null

    private val lifecycleRegistry = LifecycleRegistry(this)
    private val savedStateRegistryController = SavedStateRegistryController.create(this)
    override val savedStateRegistry: SavedStateRegistry get() = savedStateRegistryController.savedStateRegistry
    override val viewModelStore: ViewModelStore = ViewModelStore()
    override val lifecycle: Lifecycle get() = lifecycleRegistry

    override fun onCreate() {
        super.onCreate()
        savedStateRegistryController.performRestore(null)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_CREATE)
        createNotificationChannel()
        startForeground(1, createNotification())
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        setupFloatingView()
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_START)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_RESUME)
    }

    private fun setupFloatingView() {
        composeView = ComposeView(this).apply {
            setViewTreeLifecycleOwner(this@FloatingOrbService)
            setViewTreeViewModelStoreOwner(this@FloatingOrbService)
            setViewTreeSavedStateRegistryOwner(this@FloatingOrbService)
            setContent { OrbContainer() }
        }

        val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        else {
            @Suppress("DEPRECATION") WindowManager.LayoutParams.TYPE_PHONE
        }

        layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            type,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 50
            y = 200
        }

        try { windowManager.addView(composeView, layoutParams) }
        catch (e: Exception) { e.printStackTrace() }
    }

    @Composable
    fun OrbContainer() {
        val color     by OrbState.orbColor
        val message   by OrbState.message
        val listening by OrbState.isListening

        val animatedColor by animateColorAsState(
            targetValue = color,
            animationSpec = tween(500)
        )

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier
                .wrapContentSize()
                // ── Drag to move ──────────────────────────────────────────────
                .pointerInput(Unit) {
                    detectDragGestures { change, dragAmount ->
                        change.consume()
                        layoutParams?.let { p ->
                            p.x += dragAmount.x.toInt()
                            p.y += dragAmount.y.toInt()
                            windowManager.updateViewLayout(composeView, p)
                        }
                    }
                }
                // ── Tap & Long Press to capture & send ────────────────────────
                .pointerInput(Unit) {
                    detectTapGestures(
                        onTap = {
                            if (OrbState.orbColor.value != OrbState.COLOR_SENDING && OrbState.orbColor.value != OrbState.COLOR_THINKING) {
                                OrbAccessibilityService.instance?.handleOrbSingleTap()
                            }
                        },
                        onLongPress = {
                            if (OrbState.orbColor.value != OrbState.COLOR_SENDING && OrbState.orbColor.value != OrbState.COLOR_THINKING) {
                                OrbAccessibilityService.instance?.handleOrbLongPress()
                            }
                        }
                    )
                }
        ) {
            if (message.isNotEmpty()) {
                MessageBubble(message)
            }
            PremiumOrb(animatedColor, listening)
        }
    }

    @Composable
    fun MessageBubble(text: String) {
        Box(
            modifier = Modifier
                .padding(bottom = 12.dp)
                .shadow(10.dp, RoundedCornerShape(16.dp))
                .background(Color.White.copy(alpha = 0.95f), RoundedCornerShape(16.dp))
                .padding(start = 16.dp, top = 8.dp, bottom = 8.dp, end = 8.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = text, 
                    color = Color.Black, 
                    fontSize = 14.sp, 
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.weight(1f, fill = false)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Box(
                    modifier = Modifier
                        .size(24.dp)
                        .background(Color(0xFFEEEEEE), CircleShape)
                        .clickable { 
                            OrbState.message.value = ""
                            OrbAccessibilityService.instance?.stopVoice()
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Text("✕", fontSize = 12.sp, color = Color.Gray, fontWeight = FontWeight.Bold)
                }
            }
        }
    }

    @Composable
    fun PremiumOrb(color: Color, isListening: Boolean) {
        val isSpeaking by OrbState.isSpeaking
        val infiniteTransition = rememberInfiniteTransition()

        val pulseScale by infiniteTransition.animateFloat(
            initialValue = 1f,
            targetValue = when {
                color == OrbState.COLOR_DANGER     -> 1.35f
                color == OrbState.COLOR_WARNING    -> 1.3f
                color == OrbState.COLOR_THINKING   -> 1.25f // Deep smooth pulse
                color == OrbState.COLOR_HESITATION -> 1.15f
                color == OrbState.COLOR_SENDING    -> 1.25f
                isSpeaking                         -> 1.15f // Small pulse while talking
                isListening                        -> 1.25f // Bigger pulse while listening to mic
                else                               -> 1.05f
            },
            animationSpec = infiniteRepeatable(
                animation = tween(
                    durationMillis = when {
                        color == OrbState.COLOR_DANGER    -> 350
                        color == OrbState.COLOR_WARNING   -> 500
                        color == OrbState.COLOR_THINKING  -> 800 // Slower, smoother pulse
                        color == OrbState.COLOR_SENDING   -> 300
                        isSpeaking                        -> 200 // Fast micro-pulse for speech
                        isListening                       -> 400
                        else -> 1500
                    },
                    easing = FastOutSlowInEasing
                ),
                repeatMode = RepeatMode.Reverse
            )
        )

        val glowAlpha by infiniteTransition.animateFloat(
            initialValue = 0.3f,
            targetValue  = 0.75f,
            animationSpec = infiniteRepeatable(
                animation = tween(1000),
                repeatMode = RepeatMode.Reverse
            )
        )

        Box(contentAlignment = Alignment.Center) {
            // Outer Glow Ring
            Box(
                modifier = Modifier
                    .size(70.dp)
                    .scale(pulseScale)
                    .background(
                        Brush.radialGradient(listOf(color.copy(alpha = glowAlpha), Color.Transparent)),
                        CircleShape
                    )
            )
            // Inner Core
            Box(
                modifier = Modifier
                    .size(54.dp)
                    .shadow(12.dp, CircleShape)
                    .background(
                        Brush.linearGradient(listOf(color.copy(alpha = 0.8f), color)),
                        CircleShape
                    )
            )
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel("OrbServiceChannel", "AI Orb Protection", NotificationManager.IMPORTANCE_LOW)
            getSystemService(NotificationManager::class.java)?.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification =
        (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            Notification.Builder(this, "OrbServiceChannel")
        else Notification.Builder(this))
            .setContentTitle("AI Orb Active")
            .setContentText("Tap the orb anytime for help")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true)
            .build()

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_DESTROY)
        composeView?.let { windowManager.removeView(it) }
    }
}
