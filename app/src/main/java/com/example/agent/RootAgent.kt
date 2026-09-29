package com.example.agent

import android.content.Context
import android.content.Intent
import android.provider.AlarmClock
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class TimeService(private val context: Context) {
    @Tool
    fun getCurrentTime(
        @Param("Name of the city to get the time for") city: String
    ): Map<String, String> {
        val formatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        val currentTime = formatter.format(Date())
        return mapOf("city" to city, "time" to "The current time is $currentTime")
    }

    @Tool
    fun getWeather(
        @Param("Name of the city to get the weather for") city: String
    ): Map<String, String> {
        return mapOf("city" to city, "weather" to "Sunny, 25°C")
    }

    @Tool
    fun setAlarm(
        @Param("Time to set the alarm for, in 24-hour HH:mm format, e.g. '07:30'") time: String
    ): Map<String, String> {
        return try {
            // 把 "07:30" 拆成小时、分钟
            val parts = time.split(":")
            val hour = parts[0].trim().toInt()
            val minute = parts.getOrNull(1)?.trim()?.toInt() ?: 0

            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_HOUR, hour)
                putExtra(AlarmClock.EXTRA_MINUTES, minute)
                putExtra(AlarmClock.EXTRA_SKIP_UI, false) // false = 打开闹钟App界面让用户确认一下再保存
                flags = Intent.FLAG_ACTIVITY_NEW_TASK       // 不是从 Activity 直接发的，必须加这个
            }

            if (intent.resolveActivity(context.packageManager) != null) {
                context.startActivity(intent)
                mapOf("status" to "Opened the alarm app to set an alarm for $time")
            } else {
                mapOf("status" to "No alarm app found on this device")
            }
        } catch (e: Exception) {
            mapOf("status" to "Failed to set alarm: ${e.message}")
        }
    }
}

object RootAgent {
    fun create(context: Context): LlmAgent {
        val model = IntranetLlmModel(
            baseUrl = "http://10.105.1.5:4001",
            modelName = "moma_deepseek-v4-flash",
            apiKey = "sk-unaX6qDWUM3UZkz94fqYAA",
        )
        return LlmAgent(
            name = "hello_time_agent",
            description = "Tells the current time and can set alarms.",
            model = model,
            instruction = Instruction(
                "You are a helpful assistant. " +
                        "Use 'getCurrentTime' when the user asks about the time. " +
                        "Use 'setAlarm' when the user wants to set an alarm, and always confirm the time back to the user."
            ),
            tools = TimeService(context).generatedTools(),
        )
    }
}