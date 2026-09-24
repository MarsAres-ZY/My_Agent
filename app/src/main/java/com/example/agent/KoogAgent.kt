package com.example.agent

import ai.koog.agents.chatMemory.feature.ChatMemory
import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.core.tools.ToolRegistry
import ai.koog.agents.core.tools.annotations.LLMDescription
import ai.koog.agents.core.tools.annotations.Tool
import ai.koog.agents.core.tools.reflect.ToolSet
import ai.koog.http.client.ktor.KtorKoogHttpClient
import ai.koog.prompt.executor.clients.openai.OpenAIClientSettings
import ai.koog.prompt.executor.clients.openai.OpenAILLMClient
import ai.koog.prompt.executor.llms.MultiLLMPromptExecutor
import ai.koog.prompt.llm.LLMCapability
import ai.koog.prompt.llm.LLMProvider
import ai.koog.prompt.llm.LLModel
import android.content.Context
import android.content.Intent
import android.provider.AlarmClock
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@LLMDescription("时间、天气、闹钟工具")
class TimeTools(private val context: Context) : ToolSet {

    @Tool
    @LLMDescription("获取指定城市的当前时间")
    fun getCurrentTime(
        @LLMDescription("城市名") city: String
    ): String {
        val f = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        return "$city 当前时间：${f.format(Date())}"
    }

    @Tool
    @LLMDescription("获取指定城市的天气")
    fun getWeather(
        @LLMDescription("城市名") city: String
    ): String = "$city：晴，25°C"

    @Tool
    @LLMDescription("设置闹钟")
    fun setAlarm(
        @LLMDescription("24 小时制 HH:mm，例如 07:30") time: String
    ): String = try {
        val parts = time.split(":")
        val hour = parts[0].trim().toInt()
        val minute = parts.getOrNull(1)?.trim()?.toInt() ?: 0
        val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
            putExtra(AlarmClock.EXTRA_HOUR, hour)
            putExtra(AlarmClock.EXTRA_MINUTES, minute)
            putExtra(AlarmClock.EXTRA_SKIP_UI, false)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        if (intent.resolveActivity(context.packageManager) != null) {
            context.startActivity(intent)
            "已打开闹钟应用，设置 $time"
        } else {
            "设备上没有闹钟应用"
        }
    } catch (e: Exception) {
        "设置闹钟失败：${e.message}"
    }
}

object KoogAgentFactory {

    // 模型层：换成 AIBox / 其他网关只改这里
    private val executor by lazy {
        MultiLLMPromptExecutor(
            OpenAILLMClient(
                apiKey = "sk-unaX6qDWUM3UZkz94fqYAA",
                settings = OpenAIClientSettings(baseUrl = "http://10.105.1.5:4001"),
                httpClientFactory = KtorKoogHttpClient.Factory(),
            )
        )
    }

    private val llModel = LLModel(
        provider = LLMProvider.OpenAI,
        id = "moma_deepseek-v4-flash",
        capabilities = listOf(
            LLMCapability.Completion,
            LLMCapability.Temperature,
            LLMCapability.Tools,
            LLMCapability.OpenAIEndpoint.Completions,   // 关键：声明走 /chat/completions
        ),
        contextLength = 128_000,
    )

    fun create(context: Context) = AIAgent(
        promptExecutor = executor,
        llmModel = llModel,
        systemPrompt = "You are a helpful assistant. " +
                "Use 'getCurrentTime' for time questions, 'getWeather' for weather, " +
                "and 'setAlarm' to set alarms, and always confirm the time back to the user.",
        toolRegistry = ToolRegistry { tools(TimeTools(context)) },
    ){
        install(ChatMemory) {
            windowSize(20)          // 只保留最近 20 条，避免上下文无限增长
        }
    }
}