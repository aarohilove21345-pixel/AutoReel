package com.autoreel.app

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.FileObserver
import android.os.IBinder
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File

class FolderWatcherService : Service() {

    private var observer: FileObserver? = null
    private val scope = CoroutineScope(Dispatchers.IO)
    private val processed = mutableSetOf<String>()

    override fun onCreate() {
        super.onCreate()
        startForegroundServiceNotification()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val folderPath = intent?.getStringExtra("folder") ?: return START_NOT_STICKY
        val folder = File(folderPath)
        if (!folder.exists()) folder.mkdirs()

        StatusBus.post("👀 মনিটর শুরু হলো: $folderPath")
        StatusBus.setState("WATCHING")

        observer = object : FileObserver(folderPath, CLOSE_WRITE or MOVED_TO) {
            override fun onEvent(event: Int, path: String?) {
                if (path == null) return
                if (!path.endsWith(".mp4", true) && !path.endsWith(".mov", true)) return
                val file = File(folder, path)
                if (processed.contains(file.absolutePath)) return
                processed.add(file.absolutePath)
                scope.launch { processVideo(file) }
            }
        }
        observer?.startWatching()
        return START_STICKY
    }

    private fun processVideo(file: File) {
        try {
            StatusBus.setState("PROCESSING")
            StatusBus.post("⚙️ প্রসেসিং শুরু: ${file.name}")

            val prefs = getSharedPreferences("autoreel_prefs", MODE_PRIVATE)
            val provider = prefs.getString("ai_provider", "gemini") ?: "gemini"
            val aiKey = prefs.getString("ai_key", "") ?: ""
            val fbPageId = prefs.getString("fb_page_id", "") ?: ""
            val fbToken = prefs.getString("fb_token", "") ?: ""
            val ytToken = prefs.getString("yt_token", "") ?: ""

            val result = if (aiKey.isNotBlank()) {
                AiCaptionGenerator(provider, aiKey).generate(file)
            } else {
                CaptionResult("নতুন ভিডিও: ${file.nameWithoutExtension}", emptyList())
            }
            val fullCaption = (listOf(result.caption) + result.hashtags).joinToString("\n\n")
            StatusBus.post("✍️ ক্যাপশন তৈরি হলো:\n$fullCaption")

            StatusBus.setState("UPLOADING")

            if (fbPageId.isNotBlank() && fbToken.isNotBlank()) {
                StatusBus.post("⬆️ Facebook-এ আপলোড হচ্ছে...")
                val fbId = FacebookUploader(fbPageId, fbToken).upload(file, fullCaption)
                StatusBus.post("✅ Facebook আপলোড সফল, video id: $fbId")
            }

            if (ytToken.isNotBlank()) {
                StatusBus.post("⬆️ YouTube-এ আপলোড হচ্ছে...")
                val ytId = YouTubeUploader(ytToken).upload(file, result.caption, fullCaption)
                StatusBus.post("✅ YouTube আপলোড সফল, video id: $ytId")
            }

            StatusBus.setState("SUCCESS")
            StatusBus.post("🎉 সম্পন্ন: ${file.name}")
        } catch (e: Exception) {
            StatusBus.setState("ERROR")
            StatusBus.post("❌ সমস্যা: ${e.message}")
        }
    }

    private fun startForegroundServiceNotification() {
        val channelId = "autoreel_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "AutoReel Service", NotificationManager.IMPORTANCE_LOW
            )
            (getSystemService(NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(channel)
        }
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("AutoReel চলছে")
            .setContentText("ফোল্ডার মনিটর করা হচ্ছে...")
            .setSmallIcon(android.R.drawable.ic_menu_upload)
            .build()
        startForeground(1, notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        observer?.stopWatching()
        StatusBus.setState("STOPPED")
        StatusBus.post("⏹️ মনিটরিং বন্ধ হলো")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
