package com.example.agent

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.agent.databinding.ActivityMainBinding
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
