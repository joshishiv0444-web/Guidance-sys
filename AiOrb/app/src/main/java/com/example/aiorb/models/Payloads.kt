package com.example.aiorb.models

import com.google.gson.annotations.SerializedName

// ─── Guidance Models ────────────────────────────────────────────────────────
data class GuidanceRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("user_query") val userQuery: String,
    @SerializedName("screen_context") val screenContext: Any, // Can be String or Map/List (we'll send JSON String or ElementMappingContext)
    @SerializedName("risk_level") val riskLevel: String = "LOW"
)

data class GuidanceResponse(
    @SerializedName("output") val output: String,
    @SerializedName("voice_output") val voiceOutput: String,
    @SerializedName("hard_stop") val hardStop: Boolean,
    @SerializedName("fraud_risk") val fraudRisk: String,
    @SerializedName("rag_used") val ragUsed: Boolean
)

// ─── URL Fraud Models ───────────────────────────────────────────────────────
data class URLRequest(
    @SerializedName("url") val url: String
)

data class URLResponse(
    @SerializedName("url") val url: String,
    @SerializedName("url_reputation") val urlReputation: String
)

// ─── Scam Models ────────────────────────────────────────────────────────────
data class ScamRequest(
    @SerializedName("screen_context") val screenContext: Any
)

data class ScamResponse(
    @SerializedName("model_prob") val modelProb: Double?,
    @SerializedName("label") val label: String?,
    @SerializedName("risk_level") val riskLevel: String?
)

// ─── Internal Helper Models ─────────────────────────────────────────────────
data class ElementMappingContext(
    @SerializedName("screen") val screen: String,
    @SerializedName("elements") val elements: List<String>
)

data class UIElement(
    val type: String,      // "input" | "button" | "text"
    val id: String,
    val text: String,
    val isClickable: Boolean,
    val isEditable: Boolean,
    val bounds: String
) {
    // Converts to a human-readable label for the elements[] arrays
    fun toLabel(): String {
        return when {
            isEditable && text.isNotBlank()   -> "$text input"
            isEditable                        -> "Input field"
            isClickable && text.isNotBlank()  -> "${text} button"
            text.isNotBlank()                 -> text
            else                              -> type
        }
    }
}

// ─── UX Analytics Sync Models ───────────────────────────────────────────────
data class FrictionPayload(
    @SerializedName("app") val app: String,
    @SerializedName("screen") val screen: String = "Overall",
    @SerializedName("avgHesitation") val avgHesitation: Int,
    @SerializedName("oscillationRate") val oscillationRate: Int
)
