import json
import os
import time
import requests
from config.config import NEW_POSTS_FILE, LABELED_POSTS_FILE, GOOGLE_API_KEY

GENIE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}
RATE_LIMIT_DELAY = 5

# ✅ Load new_posts.json
def load_new_posts():
    if not os.path.exists(NEW_POSTS_FILE):
        print(f"[ERROR] {NEW_POSTS_FILE} not found!")
        return []
    with open(NEW_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ Load labeled_posts.json
def load_labeled_posts():
    if os.path.exists(LABELED_POSTS_FILE):
        with open(LABELED_POSTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# ✅ Save labeled videos
def save_label(video, label):
    labeled = load_labeled_posts()
    video_out = {
        "url": video.get("url", ""),
        "title": video.get("title", ""),
        "channel": video.get("channelName", ""),
        "date": video.get("date", ""),
        "views": video.get("viewCount", 0),
        "likes": video.get("likes", 0),
        "category": label.get("category", "Unknown"),
        "subject": label.get("subject", "Unknown"),
        "text": video.get("text", "")
    }
    labeled.append(video_out)
    with open(LABELED_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(labeled, f, ensure_ascii=False, indent=2)
    print(f"[DEBUG] Saved label for: {video_out.get('title')[:50]}")

# ✅ Clean Gemini output and ensure valid JSON
def clean_json_output(output_text):
    # Remove code fences
    if output_text.startswith("```"):
        output_text = output_text.strip("`")
        if output_text.lower().startswith("json"):
            output_text = output_text[4:].strip()

    # Remove reasoning sections (anything after a closing curly brace)
    if "}" in output_text:
        output_text = output_text.split("}")[0] + "}"

    return output_text.strip()

# ✅ Classify video
def classify_video(video, idx):
    text = video.get("text", "") or video.get("title", "")
    if not text.strip():
        print(f"[DEBUG][{idx}] Empty video text, skipping…")
        return {"category": "Other", "subject": "Unknown"}

    prompt = (
        "Classify this YouTube video strictly as a JSON object with keys "
        "`category` and `subject`. "
        "Return ONLY one JSON object, no lists, no extra text.\n\n"
        f"Video content:\n{text}"
    )

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    url = f"{GENIE_URL}?key={GOOGLE_API_KEY}"

    for attempt in range(5):
        r = requests.post(url, headers=HEADERS, json=body)

        if r.status_code == 429:
            wait_time = 30
            print(f"[DEBUG][{idx}] Rate limit, waiting {wait_time}s…")
            time.sleep(wait_time)
            continue

        if r.status_code != 200:
            print(f"[DEBUG][{idx}] HTTP {r.status_code}: {r.text}")
            return {"category": "Error", "subject": "Error"}

        try:
            data = r.json()
            output_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"[DEBUG][{idx}] Output: {output_text}")

            output_text = clean_json_output(output_text)
            parsed = json.loads(output_text)

            # ✅ If list returned, take the first item
            if isinstance(parsed, list) and len(parsed) > 0:
                parsed = parsed[0]

            # ✅ Ensure it's a dict
            if not isinstance(parsed, dict):
                return {"category": "Other", "subject": "Unknown"}

            return parsed

        except Exception as e:
            print(f"[DEBUG][{idx}] Failed to parse: {e}")
            return {"category": "Other", "subject": "Unknown"}

    return {"category": "Other", "subject": "Unknown"}

# ✅ Main
def main():
    videos = load_new_posts()
    labeled = load_labeled_posts()
    done_urls = {item.get("url") for item in labeled}

    print(f"[INFO] Loaded {len(videos)} videos")

    for idx, video in enumerate(videos):
        if video.get("url") in done_urls:
            continue  # Skip already processed

        labels = classify_video(video, idx)
        save_label(video, labels)
        time.sleep(RATE_LIMIT_DELAY)

    print("[INFO] Classification completed.")

if __name__ == "__main__":
    main()
