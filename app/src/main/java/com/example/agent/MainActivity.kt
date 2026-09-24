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
import com.google.firebase.Firebase
import com.google.firebase.appcheck.appCheck
import com.google.firebase.appcheck.debug.DebugAppCheckProviderFactory
import com.google.firebase.appcheck.playintegrity.PlayIntegrityAppCheckProviderFactory
import com.google.firebase.initialize
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val agent by lazy { KoogAgentFactory.create(applicationContext) }
    private val sessionId = "session-123"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.sendButton.setOnClickListener {
            val userInput = binding.inputEditText.text?.toString().orEmpty()
            if (userInput.isNotBlank()) {
                askKoogAgent(userInput)
                binding.inputEditText.text = null
            }
        }
    }

    private fun askKoogAgent(userInput: String) {
        binding.resultTextView.text = "思考中…"
        lifecycleScope.launch {
            binding.resultTextView.text = try {
                agent.run(userInput,sessionId)
            } catch (e: Exception) {
                "出错：${e.message}"
            }
        }
    }
}
