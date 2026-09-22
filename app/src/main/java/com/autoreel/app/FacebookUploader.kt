package com.autoreel.app

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.util.concurrent.TimeUnit

class FacebookUploader(
    private val pageId: String,
    private val pageAccessToken: String
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.MINUTES)
        .readTimeout(10, TimeUnit.MINUTES)
        .build()

    fun upload(videoFile: File, description: String): String {
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("access_token", pageAccessToken)
            .addFormDataPart("description", description)
            .addFormDataPart("source", videoFile.name, videoFile.asRequestBody("video/mp4".toMediaType()))
            .build()

        val req = Request.Builder()
            .url("https://graph-video.facebook.com/v19.0/$pageId/videos")
            .post(requestBody)
            .build()

        client.newCall(req).execute().use { resp ->
            val text = resp.body?.string() ?: ""
            if (!resp.isSuccessful) throw RuntimeException("Facebook upload failed: $text")
            return JSONObject(text).optString("id", "unknown")
        }
    }
}
