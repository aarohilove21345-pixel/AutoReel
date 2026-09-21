"""
facebook_uploader.py
Facebook Graph API দিয়ে Page-এ ভিডিও পোস্ট করে।
"""
import requests

GRAPH_VIDEO_URL = "https://graph-video.facebook.com/v19.0"


def upload_video(page_id, page_access_token, file_path, description=""):
    if not page_id or not page_access_token:
        raise ValueError("Facebook Page ID / Access Token খালি আছে।")

    url = f"{GRAPH_VIDEO_URL}/{page_id}/videos"
    with open(file_path, "rb") as f:
        files = {"source": f}
        data = {"description": description, "access_token": page_access_token}
        resp = requests.post(url, files=files, data=data, timeout=900)

    if resp.status_code != 200:
        raise RuntimeError(f"Facebook upload failed: {resp.text}")
    return resp.json().get("id", "")
