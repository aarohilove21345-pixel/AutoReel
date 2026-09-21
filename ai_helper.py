"""
ai_helper.py
Claude API দিয়ে ক্যাপশন এবং হ্যাশট্যাগ জেনারেট করে (pure requests, Android-compatible)।
"""
import requests

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL = "claude-sonnet-4-6"


def _call_claude(api_key, prompt, max_tokens=200):
    if not api_key:
        raise ValueError("Anthropic API key খালি। Settings থেকে দাও।")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(ANTHROPIC_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    return "\n".join(parts).strip()


def generate_caption(api_key, video_filename):
    prompt = (
        f"Write one short, catchy social media caption (max 2 sentences, no hashtags, "
        f"no quotation marks) for a short video file named '{video_filename}'. "
        f"Return ONLY the caption text."
    )
    return _call_claude(api_key, prompt, max_tokens=120)


def generate_hashtags(api_key, video_filename, caption=""):
    prompt = (
        f"Suggest 8 to 12 relevant, high-reach hashtags for a short video named "
        f"'{video_filename}' with caption: '{caption}'. Return ONLY hashtags "
        f"separated by single spaces, each starting with #."
    )
    return _call_claude(api_key, prompt, max_tokens=100)
