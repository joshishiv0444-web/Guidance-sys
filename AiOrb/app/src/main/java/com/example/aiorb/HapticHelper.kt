package com.example.aiorb

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.util.Log

object HapticHelper {

    private fun getVibrator(context: Context): Vibrator? {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vm = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
                vm?.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
            }
        } catch (e: Exception) {
            Log.w("HapticHelper", "Could not get vibrator: ${e.message}")
            null
        }
    }

    private fun vibrate(context: Context, pattern: LongArray, repeat: Int = -1) {
        try {
            val vibrator = getVibrator(context) ?: return
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createWaveform(pattern, repeat))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(pattern, repeat)
            }
        } catch (e: Exception) {
            // Silently ignore — vibration is a nice-to-have, never crash for it
            Log.w("HapticHelper", "Vibration skipped: ${e.message}")
        }
    }

    fun warningHaptic(context: Context) {
        // Short sharp triple pulse for danger
        vibrate(context, longArrayOf(0, 100, 50, 100, 50, 100))
    }

    fun hesitationHaptic(context: Context) {
        // Soft single pulse for gentle alert
        vibrate(context, longArrayOf(0, 60))
    }
}
