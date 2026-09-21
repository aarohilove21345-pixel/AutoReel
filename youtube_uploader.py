"""
youtube_uploader.py
python-for-android বিল্ডে google-api-python-client কম্পাইল করা কঠিন, তাই এখানে
শুধু 'requests' দিয়ে YouTube Data API v3-এ সরাসরি HTTP কল করা হয়েছে।

Settings-এ যা লাগবে:
  - youtube_client_id, youtube_client_secret  -> Google Cloud OAuth Client
  - youtube_refresh_token -> OAuth Playground দিয়ে একবার জেনারেট করে নিতে হবে
"""
import json
import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def _get_access_token(client_id, client_secret, refresh_token):
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_video(client_id, client_secret, refresh_token, file_path,
                  title, description="", tags=None):
    if not client_id or not client_secret or not refresh_token:
        raise ValueError("YouTube client_id / client_secret / refresh_token খালি আছে।")

    access_token = _get_access_token(client_id, client_secret, refresh_token)

    metadata = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": "22",
        },
        "status": {"privacyStatus": "public"},
    }

    boundary = "autoreel_boundary_xyz"
    with open(file_path, "rb") as f:
        video_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: video/*\r\n\r\n"
    ).encode("utf-8") + video_bytes + f"\r\n--{boundary}--".encode("utf-8")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": f"multipart/related; boundary={boundary}",
    }
    params = {"uploadType": "multipart", "part": "snippet,status"}

    resp = requests.post(UPLOAD_URL, params=params, headers=headers, data=body, timeout=900)
    if resp.status_code >= 300:
        raise RuntimeError(f"YouTube upload failed: {resp.text}")
    return resp.json().get("id")
