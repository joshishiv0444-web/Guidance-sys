package com.example.aiorb.models

data class AppTelemetry(
    val packageName: String,
    var openCount: Int = 0,
    var helpRequestCount: Int = 0
) {
    // 0.0 to 1.0 (1.0 means high trust, 0.0 means high struggle)
    val trustRating: Float
        get() {
            if (openCount == 0) return 1f
            // If they ask for help more than they open the app, trust is 0.
            val ratio = helpRequestCount.toFloat() / openCount.toFloat()
            return (1f - ratio).coerceIn(0f, 1f)
        }
        
    val displayRating: String
        get() {
            val percentage = (trustRating * 100).toInt()
            return "$percentage% Trust"
        }
}
