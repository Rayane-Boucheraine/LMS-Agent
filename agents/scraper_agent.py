import requests
import json
import os
from datetime import datetime
from config.config import (
    APIFY_API_TOKEN,
    APIFY_DATASET_ID,
    LAST_UPDATE_FILE,
    RAW_POSTS_FILE,  # ممكن تبدل الاسم لـ RAW_VIDEOS_FILE
    NEW_POSTS_FILE   # ممكن تبدل الاسم لـ NEW_VIDEOS_FILE
)

# ✅ Load last update timestamp
def load_last_update():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as f:
            return f.read().strip()
    return "1970-01-01T00:00:00.000Z"

# ✅ Save last update timestamp
def save_last_update(timestamp):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(timestamp)

# ✅ Fetch videos from Apify dataset
def fetch_videos():
    url = f"https://api.apify.com/v2/datasets/{APIFY_DATASET_ID}/items?token={APIFY_API_TOKEN}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# ✅ Save JSON to file
def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ Parse ISO datetime
def parse_time(t):
    return datetime.fromisoformat(t.replace("Z", "+00:00"))

if __name__ == "__main__":
    last_update = load_last_update()
    all_videos = fetch_videos()

    # Save all raw videos
    save_json(RAW_POSTS_FILE, all_videos)

    # ✅ Filter new videos by date
    new_videos = [
        vid for vid in all_videos
        if parse_time(vid.get("date", "1970-01-01T00:00:00.000Z")) > parse_time(last_update)
    ]

    if new_videos:
        save_json(NEW_POSTS_FILE, new_videos)
        latest_time = max(vid["date"] for vid in new_videos)
        save_last_update(latest_time)
        print(f"✅ {len(new_videos)} new videos fetched")
    else:
        save_json(NEW_POSTS_FILE, [])
        print("✅ 0 new videos fetched")
