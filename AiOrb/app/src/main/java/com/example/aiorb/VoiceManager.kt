package com.example.aiorb

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import java.util.*

class VoiceManager(private val context: Context, private var isHindi: Boolean = false) : TextToSpeech.OnInitListener {

    private var tts: TextToSpeech? = null
    private var speechRecognizer: SpeechRecognizer? = null

    var isTtsReady = false
    var onSpeechEnd: ((String?) -> Unit)? = null

    init {
        tts = TextToSpeech(context, this)
        if (SpeechRecognizer.isRecognitionAvailable(context)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
            setupSpeechRecognizer()
        } else {
            Log.e("SafeAssist_Voice", "Speech recognition is not available on this device.")
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            applyCurrentLanguage()
            if (isTtsReady) {
                isTtsReady = true
                tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {
                        OrbState.isSpeaking.value = true
                    }
                    override fun onDone(utteranceId: String?) {
                        OrbState.isSpeaking.value = false
                    }
                    @Deprecated("Deprecated in Java")
                    override fun onError(utteranceId: String?) {
                        OrbState.isSpeaking.value = false
                    }
                })
            }
        }
    }

    fun setLanguage(isHindi: Boolean) {
        this.isHindi = isHindi
        applyCurrentLanguage()
    }

    private fun applyCurrentLanguage() {
        val locale = if (isHindi) Locale("hi", "IN") else Locale.US
        val result = tts?.setLanguage(locale)
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            Log.e("SafeAssist_Voice", "TTS Language not supported for locale $locale")
            isTtsReady = false
        } else {
            isTtsReady = true
        }
    }

    private fun setupSpeechRecognizer() {
        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            
            override fun onError(error: Int) {
                Log.e("SafeAssist_Voice", "SpeechRecognizer error: $error")
                OrbState.isListening.value = false
                onSpeechEnd?.invoke(null) // null means error/timeout
            }

            override fun onResults(results: Bundle?) {
                OrbState.isListening.value = false
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val text = matches?.firstOrNull()
                onSpeechEnd?.invoke(text)
            }

            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
    }

    fun speak(text: String) {
        if (isTtsReady) {
            // Stop any ongoing speech and play new one
            tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "AI_RESPONSE_${System.currentTimeMillis()}")
        }
    }

    fun stopSpeaking() {
        tts?.stop()
        OrbState.isSpeaking.value = false
    }

    fun startListening(onResult: (String?) -> Unit) {
        this.onSpeechEnd = onResult
        
        // Stop TTS if AI was talking
        stopSpeaking()

        OrbState.isListening.value = true
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            val locale = if (isHindi) Locale("hi", "IN") else Locale.US
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, locale.toString())
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            // Give the user more time to pause between words before cutting them off
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 3000L)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 3000L)
        }
        try {
            speechRecognizer?.startListening(intent)
        } catch (e: Exception) {
            Log.e("SafeAssist_Voice", "Failed to start listening: ${e.message}")
            OrbState.isListening.value = false
            onResult(null)
        }
    }

    fun destroy() {
        tts?.stop()
        tts?.shutdown()
        speechRecognizer?.destroy()
    }
}
