package com.example.agent

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioTrack
import com.google.firebase.ai.type.InlineDataPart

suspend fun speak(text: String) {
    val response = TtsProvider.ttsModel.generateContent(text)
    val part = response.candidates.firstOrNull()
        ?.content?.parts?.firstOrNull() as? InlineDataPart ?: return

    val pcmData = part.inlineData // ByteArray
    playPcmAudio(pcmData)
}

private fun playPcmAudio(pcmData: ByteArray) {
    val sampleRate = 24000 // Gemini TTS 默认采样率，如遇播放异常(变调/破音)可尝试改成实际返回的采样率
    val audioTrack = AudioTrack(
        AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_MEDIA)
            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
            .build(),
        AudioFormat.Builder()
            .setSampleRate(sampleRate)
            .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
            .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
            .build(),
        pcmData.size,
        AudioTrack.MODE_STATIC,
        AudioManager.AUDIO_SESSION_ID_GENERATE
    )
    audioTrack.write(pcmData, 0, pcmData.size)
    audioTrack.play()
}