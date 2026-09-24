package com.example.agent

import com.google.adk.kt.models.LlmRequest
import com.google.adk.kt.models.LlmResponse
import com.google.adk.kt.models.Model
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.FunctionCall          // ⚠️ 按实际类名核对
import com.google.adk.kt.types.FunctionResponse      // ⚠️ 按实际类名核对
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.header
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.add
import kotlinx.serialization.json.booleanOrNull
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.doubleOrNull
import kotlinx.serialization.json.longOrNull
import kotlinx.serialization.json.put
import kotlinx.serialization.json.putJsonArray
import kotlinx.serialization.json.putJsonObject

// ---------- OpenAI 协议数据类 ----------
@Serializable
data class ChatMessage(
    val role: String,
    val content: String? = null,
    val tool_calls: List<OaToolCall>? = null,
    val tool_call_id: String? = null,
)

@Serializable data class OaToolCall(val id: String, val type: String = "function", val function: FnCall)
@Serializable data class FnCall(val name: String, val arguments: String)   // arguments 是 JSON 字符串

@Serializable data class ToolDef(val type: String = "function", val function: FnDef)
@Serializable data class FnDef(val name: String, val description: String, val parameters: JsonObject)

@Serializable
data class ChatRequest(
    val model: String,
    val messages: List<ChatMessage>,
    val tools: List<ToolDef>? = null,
    val stream: Boolean = false,
)

@Serializable data class ChatChoice(val message: ChatMessage)
@Serializable data class ChatResponse(val choices: List<ChatChoice>)

// ---------- 工具函数 ----------
private fun Any?.toJsonElement(): JsonElement = when (this) {
    null -> JsonNull
    is JsonElement -> this
    is Boolean -> JsonPrimitive(this)
    is Number -> JsonPrimitive(this)
    is String -> JsonPrimitive(this)
    is Map<*, *> -> JsonObject(entries.associate { (k, v) -> k.toString() to v.toJsonElement() })
    is Iterable<*> -> JsonArray(map { it.toJsonElement() })
    else -> JsonPrimitive(toString())
}

private fun JsonElement.toKotlin(): Any? = when (this) {
    is JsonNull -> null
    is JsonPrimitive -> if (isString) content else (booleanOrNull ?: longOrNull ?: doubleOrNull ?: content)
    is JsonObject -> mapValues { it.value.toKotlin() }
    is JsonArray -> map { it.toKotlin() }
}

private fun parseArgs(json: String): Map<String, Any?> {
    val obj = runCatching { Json.parseToJsonElement(json) as? JsonObject }.getOrNull()
    return obj?.mapValues { it.value.toKotlin() } ?: emptyMap<String, Any?>()
}

private fun schema(paramName: String, paramDesc: String): JsonObject = buildJsonObject {
    put("type", "object")
    putJsonObject("properties") {
        putJsonObject(paramName) {
            put("type", "string")
            put("description", paramDesc)
        }
    }
    putJsonArray("required") { add(paramName) }
}

class IntranetLlmModel(
    private val baseUrl: String,
    private val modelName: String,
    private val apiKey: String,
) : Model {

    override val name: String = modelName

    // 手写工具声明，名称必须与 @Tool 方法名一致
    private val toolDefs: List<ToolDef> = listOf(
        ToolDef(function = FnDef("getCurrentTime", "Get the current time of a city",
            schema("city", "Name of the city to get the time for"))),
        ToolDef(function = FnDef("getWeather", "Get the weather of a city",
            schema("city", "Name of the city to get the weather for"))),
        ToolDef(function = FnDef("setAlarm", "Set an alarm",
            schema("time", "Time in 24-hour HH:mm format, e.g. '07:30'"))),
    )

    private val client = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                encodeDefaults = true
                explicitNulls = false
            })
        }
        install(HttpTimeout) {
            requestTimeoutMillis = 60_000
            connectTimeoutMillis = 15_000
            socketTimeoutMillis = 60_000
        }
    }

    private fun toChatMessages(request: LlmRequest): List<ChatMessage> {
        val out = mutableListOf<ChatMessage>()
        for (c in request.contents) {
            val text = c.parts.mapNotNull { it.text }.joinToString("")
            val calls = c.parts.mapNotNull { it.functionCall }
            val responses = c.parts.mapNotNull { it.functionResponse }
            when {
                calls.isNotEmpty() -> out += ChatMessage(
                    role = "assistant",
                    content = text.ifEmpty { null },
                    tool_calls = calls.map { fc ->
                        val n = fc.name.orEmpty()
                        OaToolCall(
                            id = fc.id ?: "call_$n",
                            function = FnCall(n, (fc.args ?: emptyMap<String, Any?>()).toJsonElement().toString()),
                        )
                    },
                )
                responses.isNotEmpty() -> responses.forEach { fr ->
                    val n = fr.name.orEmpty()
                    out += ChatMessage(
                        role = "tool",
                        tool_call_id = fr.id ?: "call_$n",
                        content = (fr.response ?: emptyMap<String, Any?>()).toJsonElement().toString(),
                    )
                }
                else -> out += ChatMessage(
                    role = if (c.role == Role.MODEL) "assistant" else "user",
                    content = text,
                )
            }
        }
        return out
    }

    override fun generateContent(request: LlmRequest, stream: Boolean): Flow<LlmResponse> = flow {
        val resp: ChatResponse = client.post("$baseUrl/v1/chat/completions") {
            contentType(ContentType.Application.Json)
            header("Authorization", "Bearer $apiKey")
            setBody(ChatRequest(
                model = modelName,
                messages = toChatMessages(request),
                tools = toolDefs,
                stream = false,
            ))
        }.body()

        val msg = resp.choices.firstOrNull()?.message
        val calls = msg?.tool_calls.orEmpty()
        val parts: List<Part> = if (calls.isNotEmpty()) {
            calls.map { tc ->
                Part(functionCall = FunctionCall(
                    id = tc.id,
                    name = tc.function.name,
                    args = parseArgs(tc.function.arguments),
                ))
            }
        } else {
            listOf(Part(text = msg?.content.orEmpty()))
        }
        emit(LlmResponse(content = Content(role = Role.MODEL, parts = parts), partial = false))
    }
}