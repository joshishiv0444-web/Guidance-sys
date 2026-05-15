package com.example.aiorb

import android.content.Context
import android.content.SharedPreferences
import com.example.aiorb.models.AppTelemetry
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

object TelemetryManager {
    private const val PREFS_NAME = "AiOrbTelemetry"
    private const val KEY_APP_STATS = "app_stats"

    private fun getPrefs(context: Context): SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    private fun getAllStats(context: Context): MutableMap<String, AppTelemetry> {
        val json = getPrefs(context).getString(KEY_APP_STATS, null) ?: return mutableMapOf()
        val type = object : TypeToken<MutableMap<String, AppTelemetry>>() {}.type
        return try {
            Gson().fromJson(json, type) ?: mutableMapOf()
        } catch (e: Exception) {
            mutableMapOf()
        }
    }

    private fun saveAllStats(context: Context, stats: Map<String, AppTelemetry>) {
        val json = Gson().toJson(stats)
        getPrefs(context).edit().putString(KEY_APP_STATS, json).apply()
    }

    // ─── Tracking ─────────────────────────────────────────────────────────────

    fun trackAppOpen(context: Context, packageName: String) {
        if (isIgnoredPackage(packageName)) return
        val stats = getAllStats(context)
        val appStat = stats[packageName] ?: AppTelemetry(packageName)
        appStat.openCount += 1
        stats[packageName] = appStat
        saveAllStats(context, stats)
    }

    fun trackHelpRequest(context: Context, packageName: String) {
        if (isIgnoredPackage(packageName)) return
        val stats = getAllStats(context)
        val appStat = stats[packageName] ?: AppTelemetry(packageName)
        appStat.helpRequestCount += 1
        stats[packageName] = appStat
        saveAllStats(context, stats)
    }

    // ─── Analytics Extraction for Dashboard/API ───────────────────────────────

    fun getTopStruggleApps(context: Context, limit: Int = 3): List<AppTelemetry> {
        return getAllStats(context).values
            .filter { it.helpRequestCount > 0 }
            .sortedByDescending { it.helpRequestCount }
            .take(limit)
    }

    fun getTopTrustedApps(context: Context, limit: Int = 3): List<AppTelemetry> {
        return getAllStats(context).values
            .filter { it.openCount > 2 } // Only consider apps opened a few times
            .sortedByDescending { it.trustRating }
            .take(limit)
    }

    fun getAllStatsRaw(context: Context): List<AppTelemetry> {
        return getAllStats(context).values.toList()
    }

    fun exportToJson(context: Context): String {
        val stats = getAllStats(context)
        return Gson().toJson(stats.values)
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    private fun isIgnoredPackage(pkg: String): Boolean {
        // Ignore launchers, system UI, and our own app
        val lower = pkg.lowercase()
        return lower.contains("launcher") || 
               lower.contains("home") || 
               lower.contains("systemui") || 
               lower == "com.example.aiorb" ||
               lower.isBlank()
    }
}
