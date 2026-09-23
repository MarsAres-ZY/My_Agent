# AI Agent 集成方案

# 1\. 方案概述

## **目标**

- 在 Android 车机 \(AAOS\) 上集成大模型能力，推理算力由 AIBox 承担

- 自然语言车控，例如："有点热，把空调调到 22 度"

- 多轮对话：具备上下文记忆

- 多模态输入：语音、触屏 UI、物理按键



## 设计原则

|原则|说明|
|---|---|
|Agent|为控制中枢：决策循环、工具执行等都在车机侧 ADK Agent 内完成|
|AIBox|只做推理，提供算力|
|协议标准化|AIBox 暴露 OpenAI 兼容 API|
|容错处理|AIBox 故障时，可切换到轻量LLM模型使基础车控仍可用|

### 期望的架构模式

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzQ0YWMyZDE4N2M3MjM0MDRiZTM2YjQ3MjZhYWM3NWFfOWFhMjkzYTE5ZDQ1OGI2Y2I4OWJlZGE2MzhiNTI1ZDRfSUQ6NzY4ODIzOTc3Njk2OTAwMTk0OF8xNzkwMTQ1OTA1OjE3OTAyMzIzMDVfVjM)

**当前制限**

ADK Kotlin 的 Model 目前仅内置 Gemini，尚未提供接入其他 LLM（OpenAI、Claude、千问等）的官方适配器。因此"AAOS 内 ADK Agent → AIBox"这条链路暂时无法直接打通。

### 由制限引出的两个方案

|方案|描述|
|---|---|
|方案 A|保留"Agent 在 AAOS 内"，模型暂用 ADK 原生支持的云端 Gemini。待 ADK 支持 OpenAI 等 model 时无缝切换|
|方案 B|将 Agent 层整体搬到 AIBox，与千问同侧对接|

**设计思路**

- 统一多路输入（语音、HMI 触控、物理按键）为单一的 UserRequest 意图对象

- 使用 ADK 的 Root Agent \+ 子 Agent 结构做意图路由，按业务（车控 / 导航 / 媒体 / 通讯）拆分职责，便于独立扩展与维护

- 通过 @Tool / @Param 注解将车辆功能 API 显式暴露给 LLM 调用

- Model 层做到可插拔，当前仅接入 Gemini，但预留切换到其他模型（端侧模型 / 本地大模型）的能力

- 支持车机算力、外部算力（AIBox）、云端算力三种部署形态，以适配多种业务场景

- 方案 B 由于 Agent 需要部署在 AIBox 侧，因此需要一个通信中间层作为桥梁来与 AIBox 中的 Agent 交互。经 RPC 发送至 AIBox Agent 服务，解析 Agent 返回的结构化指令，调用车辆功能模块 API 并触发反馈

---

# 2\. 方案 A

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MGI5ZjA2MjhlOGRhODFlYzcyOTg3NDZhMTVmY2U4ODRfZmNlYTJiMWE3ZTNiNjcwMmJjNGE5YTc0NmU3MTQxYjhfSUQ6NzY4ODI0MDA2MzYwNzczNzU3NF8xNzkwMTQ1OTA1OjE3OTAyMzIzMDVfVjM)

## 分层结构

|层级|作用|相关组件|
|---|---|---|
|① 输入层|多路输入归一化；意图统一入口|语音助手、HMI 触控交互、物理按键；统一用户输入|
|② Agent 层|ADK Kotlin，运行于车机进行任务编排|Runner、SessionService（InMemorySessionService 临时会话 / RoomSessionService 历史持久化）、Root Agent、子 Agent、Tools、Model|
|③ 模型层|云端 / 端侧 / AIBox|云端：Firebase AI Logic → Gemini API（HTTPS）；端侧：AAOS 下的轻量级模型；AIBox：千问|
|④ 车辆功能模块|Android Car API / 系统服务|车控、导航、媒体、电话、系统设置、车辆状态查询|
|⑤ 输出层|结果呈现|TTS 语音播报、HMI、车控执行反馈（状态变化 / Toast / 灯效）|

---

# 3\. 方案 B

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NWQ3YzI5ZWUyZWYyZWVlMTc4YTlhOWI3M2E4ZTA2ZDRfOWU4NjU4MzZhY2ExNzY2MjQzYzI2YzhkNDhjMTUxYTRfSUQ6NzY4ODI0MDE2OTU5Mzk4MjE3NV8xNzkwMTQ1OTA1OjE3OTAyMzIzMDVfVjM)

## 分层结构

|层级|作用|相关组件|
|---|---|---|
|① 输入层<br>|多路输入归一化|语音助手、HMI 触控交互、物理按键|
|② 通信中间层（与 Agent 交互）|用于与 AIBox 进行通信|统一意图入口；转发请求；接收 LLM 返回的结果；调用车辆模块|
|③ Agent 层|ADK Kotlin，运行于车机进行任务编排|Runner、SessionService（InMemorySessionService 临时会话 / RoomSessionService 历史持久化）、Root Agent、子 Agent、Tools、Model|
|④ 模型层|云端|Firebase AI Logic → Gemini API（HTTPS）|
|⑤ 车辆功能模块|Android Car API / 系统服务|车控、导航、媒体、电话、系统设置、车辆状态查询|
|⑥ 输出层|结果呈现|TTS 语音播报、HMI、车控执行反馈（状态变化 / Toast / 灯效）|

---

# 4\. 关键代码（当前工程：方案 A 验证 Demo）

当前工程 `My_Agent` 是方案 A 的最小可运行验证：Agent 运行在 Android 侧，模型经 Firebase AI Logic 调用云端 Gemini，通过 `@Tool` 暴露本地能力（查时间 / 设闹钟）供 LLM 调用。代码位于 `app/src/main/java/com/example/agent/`。

## 4.1 代码与分层对照

|分层|工程文件 / 类|说明|
|---|---|---|
|① 输入层|`MainActivity` 中 `sendButton` → `askAgent()`|当前仅文本输入，后续语音 / 按键统一转为同一入口|
|② Agent 层|`RootAgent.create()`、`InMemoryRunner`、`InMemorySessionService`|ADK Kotlin 编排；`LlmAgent` 挂载 Model + Instruction + Tools|
|③ 模型层|`AdkFirebase.create("gemini-3.8-flash", FirebaseAI.getInstance(...))`|Firebase AI Logic → Gemini API，模型层可插拔点|
|④ 功能模块|`TimeService`（`@Tool` / `@Param`）|对应车控 API 的挂载位置，当前用系统闹钟 Intent 演示|
|⑤ 输出层|`resultTextView`、`TtsProvider`|文本展示；TTS 模型已预留（Gemini TTS，`ResponseModality.AUDIO`）|

## 4.2 依赖配置（`app/build.gradle.kts`）

```kotlin
plugins {
    id("com.android.application")
    id("com.google.devtools.ksp") version "2.3.6"   // ADK 注解处理器（生成 generatedTools()）
    id("com.google.gms.google-services")             // Firebase 配置（google-services.json）
}

dependencies {
    implementation(platform("com.google.firebase:firebase-bom:34.18.0"))
    implementation("com.google.firebase:firebase-ai")                          // Firebase AI Logic → Gemini
    implementation("com.google.firebase:firebase-appcheck-debug")             // 调试期 App Check
    implementation("com.google.adk:google-adk-kotlin-firebase-android:1.0.0") // ADK 的 Firebase Model 适配

    implementation(libs.google.adk.kotlin.core.android)   // ADK Kotlin 核心（Agent / Runner / Session）
    ksp(libs.google.adk.kotlin.processor)                 // 解析 @Tool / @Param
}
```

> `libs.versions.toml` 中 `googleAdkKotlinCoreAndroid = "0.9.0"`。ADK 的 Model 目前只有 Firebase/Gemini 适配器，即"当前制限"一节所述的约束点。

## 4.3 工具暴露：`@Tool` / `@Param`（④ 功能模块）

车辆功能以普通 Kotlin 方法暴露给 LLM，注解中的描述文本就是 LLM 看到的 function-calling schema。返回 `Map` 会被序列化后回传给模型，用于生成最终回复。

```kotlin
class TimeService(private val context: Context) {

    @Tool
    fun getCurrentTime(
        @Param("Name of the city to get the time for") city: String
    ): Map<String, String> {
        val formatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        return mapOf("city" to city, "time" to "The current time is ${formatter.format(Date())}")
    }

    @Tool
    fun setAlarm(
        @Param("Time to set the alarm for, in 24-hour HH:mm format, e.g. '07:30'") time: String
    ): Map<String, String> {
        return try {
            val parts = time.split(":")
            val hour = parts[0].trim().toInt()
            val minute = parts.getOrNull(1)?.trim()?.toInt() ?: 0

            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_HOUR, hour)
                putExtra(AlarmClock.EXTRA_MINUTES, minute)
                putExtra(AlarmClock.EXTRA_SKIP_UI, false)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK   // 非 Activity 上下文发起，必须加
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
```

要点：

- KSP 会为带 `@Tool` 的类生成扩展方法 `generatedTools()`，直接传给 `LlmAgent(tools = ...)`。
- 对接车机时，把 `TimeService` 替换/扩展为 `HvacService`、`NavigationService` 等，内部调用 `CarPropertyManager` 等 Car API 即可，Agent 层无需改动。
- `AndroidManifest.xml` 中需声明对应权限，例如 `com.android.alarm.permission.SET_ALARM`。

## 4.4 Agent 与 Model 组装（② Agent 层 / ③ 模型层）

```kotlin
object RootAgent {
    fun create(context: Context): LlmAgent {
        // ③ 模型层：Firebase AI Logic → Gemini，这里是未来切换 AIBox / 端侧模型的唯一替换点
        val model = AdkFirebase.create(
            "gemini-3.8-flash",
            FirebaseAI.getInstance(FirebaseApp.getInstance())
        )
        // ② Agent 层：Root Agent，后续按车控 / 导航 / 媒体拆为子 Agent
        return LlmAgent(
            name = "hello_time_agent",
            description = "Tells the current time and can set alarms.",
            model = model,
            instruction = Instruction(
                "You are a helpful assistant. " +
                "Use 'getCurrentTime' when the user asks about the time. " +
                "Use 'setAlarm' when the user wants to set an alarm, and always confirm the time back to the user."
            ),
            tools = TimeService(context).generatedTools(),   // ④ 挂载功能模块
        )
    }
}
```

## 4.5 Runner 与会话：决策循环入口（② Agent 层）

`Runner` 负责"LLM 推理 → 工具调用 → 结果回填 → 再推理"的循环；`SessionService` 提供多轮上下文记忆。`userId + sessionId` 相同即复用同一会话。

```kotlin
class MainActivity : AppCompatActivity() {

    // Runner / SessionService 只创建一次，跟随 Activity / ViewModel 生命周期复用
    private val sessionService = InMemorySessionService()     // 临时会话；持久化可换 RoomSessionService
    private val runner = InMemoryRunner(
        agent = RootAgent.create(context = this),
        sessionService = sessionService,
    )

    private fun askAgent(userInput: String) {                 // ① 统一输入入口
        binding.resultTextView.text = "思考中…"
        lifecycleScope.launch {
            runner.runAsync(
                userId = "user-123",
                sessionId = "session-123",
                newMessage = Content(
                    role = Role.USER,
                    parts = listOf(Part(text = userInput)),
                ),
            ).collect { event ->                              // Flow<Event>：含工具调用、模型回复等事件
                val text = event.content?.parts?.firstOrNull()?.text
                if (!text.isNullOrBlank()) {
                    binding.resultTextView.text = text        // ⑤ 输出层：当前仅文本，可做增量拼接
                }
            }
        }
    }
}
```

## 4.6 Firebase 初始化与 App Check

Firebase AI Logic 要求 App Check 校验调用方，开发期使用 Debug Provider，上线换 Play Integrity。

```kotlin
// 开发期
Firebase.initialize(context = this)
Firebase.appCheck.installAppCheckProviderFactory(DebugAppCheckProviderFactory.getInstance())

// 生产
Firebase.appCheck.installAppCheckProviderFactory(PlayIntegrityAppCheckProviderFactory.getInstance())
```

> 车机（AAOS）通常没有 Play 服务，Play Integrity 不可用，生产环境的 App Check 方案需另行评估（见附录）。

## 4.7 输出层预留：TTS（⑤ 输出层）

已按 Gemini TTS 模型预留播报能力，尚未接入播放链路。

```kotlin
object TtsProvider {
    val ttsModel by lazy {
        Firebase.ai(backend = GenerativeBackend.googleAI())
            .generativeModel(
                modelName = "gemini-3.1-flash-tts-preview",
                generationConfig = GenerationConfig.Builder()
                    .setResponseModalities(listOf(ResponseModality.AUDIO))
                    .build()
            )
    }
}
```

## 4.8 请求处理流程

```
用户输入(文本/语音/按键)
   → MainActivity.askAgent()               ① 归一化为 Content(role=USER)
   → InMemoryRunner.runAsync()             ② 取会话历史 + 新消息
   → LlmAgent → AdkFirebase Model          ③ Firebase AI Logic → Gemini（HTTPS）
   → Gemini 返回 functionCall(setAlarm)    
   → TimeService.setAlarm() 执行            ④ 调用系统 / 车辆 API
   → 工具结果回填 → Gemini 生成自然语言回复
   → collect{ event } 更新 UI / TTS         ⑤ 输出
```

## 4.9 后续演进对照

|演进项|当前实现|目标|
|---|---|---|
|模型切换|`AdkFirebase.create(...)` 固定 Gemini|等待 ADK 提供 OpenAI 兼容 Model，改此一处即可指向 AIBox|
|意图路由|单一 `LlmAgent`|Root Agent + 子 Agent（车控 / 导航 / 媒体 / 通讯）|
|工具集|`TimeService`|按域拆分 `XxxService`，内部封装 Car API|
|会话|`InMemorySessionService`|`RoomSessionService` 持久化历史|
|输入|文本框|语音 ASR / HMI / 物理按键统一为 UserRequest|
|输出|`TextView`|TTS 播报 + HMI 反馈|

---

# 附录：待解决事项

|\#|事项|备注|
|---|---|---|
|1|ADK 能力边界确认||
|2|AAOS ↔ AIBox 通信协议||
|3|端侧轻量级模型选型、集成||
|4|AAOS 无 Play 服务时 Firebase App Check 生产方案|当前 Demo 使用 `DebugAppCheckProviderFactory`|



