package com.example.aiorb

import android.content.Context
import android.content.SharedPreferences

object SharedPrefsHelper {
    private const val PREFS_NAME = "AiOrbPrefs"
    private const val KEY_HESITATION = "hesitation"
    private const val KEY_ONBOARDING_COMPLETE = "onboarding_complete"
    private const val KEY_LANGUAGE_HINDI = "language_hindi"

    private fun getPrefs(context: Context): SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getHesitationThreshold(context: Context): Long =
        getPrefs(context).getLong(KEY_HESITATION, 15000L)

    fun saveHesitationThreshold(context: Context, thresholdMs: Long) =
        getPrefs(context).edit().putLong(KEY_HESITATION, thresholdMs).apply()

    fun isOnboardingComplete(context: Context): Boolean =
        getPrefs(context).getBoolean(KEY_ONBOARDING_COMPLETE, false)

    fun setOnboardingComplete(context: Context, complete: Boolean) =
        getPrefs(context).edit().putBoolean(KEY_ONBOARDING_COMPLETE, complete).apply()

    fun isHindiLanguage(context: Context): Boolean =
        getPrefs(context).getBoolean(KEY_LANGUAGE_HINDI, false)

    fun setHindiLanguage(context: Context, isHindi: Boolean) =
        getPrefs(context).edit().putBoolean(KEY_LANGUAGE_HINDI, isHindi).apply()
}
