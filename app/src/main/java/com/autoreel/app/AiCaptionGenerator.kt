package com.autoreel.app

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.concurrent.TimeUnit

data class CaptionResult(val caption: String, val hashtags: List<String>)

class AiCaptionGenerator(
    private val provider: String,
    private val apiKey: String
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    fun generate(videoFile: File): CaptionResult {
        val prompt = """
            তুমি একজন সোশ্যাল মিডিয়া কনটেন্ট রাইটার।
            নিচের ভিডিও ফাইলের নাম দেখে একটা আকর্ষণীয়, ছোট (২-৩ লাইন) ফেসবুক/ইউটিউব ক্যাপশন লিখো
            এবং ৮-১০টা relevant হ্যাশট্যাগ দাও।
            ফাইলের নাম: ${videoFile.name}
            উত্তর অবশ্যই এই JSON ফরম্যাটে দাও, অন্য কিছু লিখো না:
            {"caption": "...", "hashtags": ["#...", "#..."]}
        """.trimIndent()

        val raw = when (provider.lowercase()) {
            "openai" -> callOpenAi(prompt)
            "gemini" -> callGemini(prompt)
            "claude" -> callClaude(prompt)
            else -> throw IllegalArgumentException("Unknown AI provider: $provider")
        }
        return parseResult(raw)
    }

    private fun callOpenAi(prompt: String): String {
        val body = JSONObject().apply {
            put("model", "gpt-4o-mini")
            put("messages", JSONArray().put(JSONObject().put("role", "user").put("content", prompt)))
        }.toString().toRequestBody("application/json".toMediaType())

        val req = Request.Builder()
            .url("https://api.openai.com/v1/chat/completions")
            .addHeader("Authorization", "Bearer $apiKey")
            .post(body)
            .build()

        client.newCall(req).execute().use { resp ->
            val text = resp.body?.string() ?: throw RuntimeException("Empty OpenAI response")
            if (!resp.isSuccessful) throw RuntimeException("OpenAI error: $text")
            return JSONObject(text).getJSONArray("choices").getJSONObject(0)
                .getJSONObject("message").getString("content")
        }
    }

    private fun callGemini(prompt: String): String {
        val body = JSONObject().apply {
            put("contents", JSONArray().put(
                JSONObject().put("parts", JSONArray().put(JSONObject().put("text", prompt)))
            ))
        }.toString().toRequestBody("application/json".toMediaType())

        val req = Request.Builder()
            .url("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$apiKey")
            .post(body)
            .build()

        client.newCall(req).execute().use { resp ->
            val text = resp.body?.string() ?: throw RuntimeException("Empty Gemini response")
            if (!resp.isSuccessful) throw RuntimeException("Gemini error: $text")
            return JSONObject(text).getJSONArray("candidates").getJSONObject(0)
                .getJSONObject("content").getJSONArray("parts").getJSONObject(0).getString("text")
        }
    }

    private fun callClaude(prompt: String): String {
        val body = JSONObject().apply {
            put("model", "claude-sonnet-4-6")
            put("max_tokens", 500)
            put("messages", JSONArray().put(JSONObject().put("role", "user").put("content", prompt)))
        }.toString().toRequestBody("application/json".toMediaType())

        val req = Request.Builder()
            .url("https://api.anthropic.com/v1/messages")
            .addHeader("x-api-key", apiKey)
            .addHeader("anthropic-version", "2023-06-01")
            .post(body)
            .build()

        client.newCall(req).execute().use { resp ->
            val text = resp.body?.string() ?: throw RuntimeException("Empty Claude response")
            if (!resp.isSuccessful) throw RuntimeException("Claude error: $text")
            return JSONObject(text).getJSONArray("content").getJSONObject(0).getString("text")
        }
    }

    private fun parseResult(raw: String): CaptionResult {
        val cleaned = raw.trim().removePrefix("```json").removePrefix("```").removeSuffix("```").trim()
        return try {
            val json = JSONObject(cleaned)
            val caption = json.getString("caption")
            val tagsArr = json.getJSONArray("hashtags")
            val tags = (0 until tagsArr.length()).map { tagsArr.getString(it) }
            CaptionResult(caption, tags)
        } catch (e: Exception) {
            CaptionResult(cleaned, emptyList())
        }
    }
}
