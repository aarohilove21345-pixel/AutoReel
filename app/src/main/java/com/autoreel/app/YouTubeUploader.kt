package com.autoreel.app

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.concurrent.TimeUnit

class YouTubeUploader(private val accessToken: String) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.MINUTES)
        .readTimeout(15, TimeUnit.MINUTES)
        .build()

    fun upload(videoFile: File, title: String, description: String): String {
        val metadata = JSONObject().apply {
            put("snippet", JSONObject().apply {
                put("title", title)
                put("description", description)
                put("tags", JSONArray())
            })
            put("status", JSONObject().put("privacyStatus", "public"))
        }

        val initReq = Request.Builder()
            .url("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status")
            .addHeader("Authorization", "Bearer $accessToken")
            .addHeader("X-Upload-Content-Type", "video/mp4")
            .post(metadata.toString().toRequestBody("application/json".toMediaType()))
            .build()

        val uploadUrl = client.newCall(initReq).execute().use { resp ->
            if (!resp.isSuccessful) throw RuntimeException("YouTube init failed: ${resp.body?.string()}")
            resp.header("Location") ?: throw RuntimeException("No upload URL returned")
        }

        val uploadReq = Request.Builder()
            .url(uploadUrl)
            .put(videoFile.asRequestBody("video/mp4".toMediaType()))
            .build()

        client.newCall(uploadReq).execute().use { resp ->
            val text = resp.body?.string() ?: ""
            if (!resp.isSuccessful) throw RuntimeException("YouTube upload failed: $text")
            return JSONObject(text).optString("id", "unknown")
        }
    }
}
