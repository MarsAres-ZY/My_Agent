package com.example.agent

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.agent.databinding.ActivityMainBinding
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    // Runner 和 SessionService 通常只需要创建一次，
    // 可以放在 Activity / ViewModel 的生命周期内复用
    private val sessionService = InMemorySessionService()
    private val runner = InMemoryRunner(
        agent = RootAgent.create(context = this),
        sessionService = sessionService,
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.sendButton.setOnClickListener {
            val userInput = binding.inputEditText.text?.toString().orEmpty()
            if (userInput.isNotBlank()) {
                askAgent(userInput)
            }
        }
    }

    private fun askAgent(userInput: String) {
        binding.resultTextView.text = "思考中…"

        lifecycleScope.launch {
            runner.runAsync(
                userId = "user-123",
                sessionId = "session-123",
                newMessage = Content(
                    role = Role.USER,
                    parts = listOf(Part(text = userInput)),
                ),
            ).collect { event ->
                val text = event.content?.parts?.firstOrNull()?.text
                if (!text.isNullOrBlank()) {
                    // 简单起见直接覆盖显示，真实场景可以做增量拼接/打字机效果
                    binding.resultTextView.text = text
                }
            }
        }
    }
}
