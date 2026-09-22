package com.autoreel.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var etFolder: EditText
    private lateinit var etAiProvider: EditText
    private lateinit var etAiKey: EditText
    private lateinit var etFbPageId: EditText
    private lateinit var etFbToken: EditText
    private lateinit var etYtToken: EditText
    private lateinit var tvStatus: TextView
    private lateinit var tvLog: TextView

    private val prefs by lazy { getSharedPreferences("autoreel_prefs", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etFolder = findViewById(R.id.etFolder)
        etAiProvider = findViewById(R.id.etAiProvider)
        etAiKey = findViewById(R.id.etAiKey)
        etFbPageId = findViewById(R.id.etFbPageId)
        etFbToken = findViewById(R.id.etFbToken)
        etYtToken = findViewById(R.id.etYtToken)
        tvStatus = findViewById(R.id.tvStatus)
        tvLog = findViewById(R.id.tvLog)

        loadSettings()
        requestPermissionsIfNeeded()

        StatusBus.log.observe(this) { line -> tvLog.append("$line\n") }
        StatusBus.state.observe(this) { state -> tvStatus.text = "স্ট্যাটাস: $state" }

        findViewById<Button>(R.id.btnSave).setOnClickListener { saveSettings() }

        findViewById<Button>(R.id.btnStart).setOnClickListener {
            saveSettings()
            val folder = etFolder.text.toString().ifBlank {
                File(getExternalFilesDir(null), "Incoming").absolutePath
            }
            val intent = Intent(this, FolderWatcherService::class.java)
            intent.putExtra("folder", folder)
            ContextCompat.startForegroundService(this, intent)
        }

        findViewById<Button>(R.id.btnStop).setOnClickListener {
            stopService(Intent(this, FolderWatcherService::class.java))
        }
    }

    private fun loadSettings() {
        val defaultFolder = File(getExternalFilesDir(null), "Incoming").absolutePath
        etFolder.setText(prefs.getString("folder", defaultFolder))
        etAiProvider.setText(prefs.getString("ai_provider", "gemini"))
        etAiKey.setText(prefs.getString("ai_key", ""))
        etFbPageId.setText(prefs.getString("fb_page_id", ""))
        etFbToken.setText(prefs.getString("fb_token", ""))
        etYtToken.setText(prefs.getString("yt_token", ""))
    }

    private fun saveSettings() {
        prefs.edit()
            .putString("folder", etFolder.text.toString())
            .putString("ai_provider", etAiProvider.text.toString().trim())
            .putString("ai_key", etAiKey.text.toString().trim())
            .putString("fb_page_id", etFbPageId.text.toString().trim())
            .putString("fb_token", etFbToken.text.toString().trim())
            .putString("yt_token", etYtToken.text.toString().trim())
            .apply()
        tvStatus.text = "সেটিংস সংরক্ষণ হয়েছে ✅"
    }

    private fun requestPermissionsIfNeeded() {
        val perms = mutableListOf<String>()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            perms.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val toRequest = perms.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (toRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, toRequest.toTypedArray(), 100)
        }
    }
}
