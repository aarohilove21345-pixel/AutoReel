"""
storage_helper.py
Android-এ ফোনের ভিতরেই JSON ফাইলে সেটিংস আর হিস্ট্রি সেভ রাখে।
"""
import json
import os
from datetime import datetime

try:
    from android.storage import app_storage_path
    BASE_DIR = app_storage_path()
except Exception:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")

DEFAULT_CONFIG = {
    "youtube_client_id": "",
    "youtube_client_secret": "",
    "youtube_refresh_token": "",
    "facebook_page_id": "",
    "facebook_page_access_token": "",
    "anthropic_api_key": "",
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    return merged


def save_config(cfg):
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def add_history(filename, platforms, status, error=""):
    entries = load_history()
    entries.insert(0, {
        "filename": filename,
        "platforms": platforms,
        "status": status,
        "error": error,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
