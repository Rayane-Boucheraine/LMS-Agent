import json
import os
import time
import requests
from config.config import RAW_POSTS_FILE, LABELED_POSTS_FILE, GOOGLE_API_KEY

GENIE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}
RATE_LIMIT_DELAY = 5

# ✅ تحميل raw posts
def load_raw_posts():
    if not os.path.exists(RAW_POSTS_FILE):
        print(f"[ERROR] {RAW_POSTS_FILE} not found!")
        return []
    with open(RAW_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ تحميل labeled posts (list)
def load_labeled_posts():
    if os.path.exists(LABELED_POSTS_FILE):
        with open(LABELED_POSTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# ✅ حفظ مباشرة بنفس الشكل الحالي
def save_label(post, label):
    labeled = load_labeled_posts()
    post_out = {
        "url": post.get("url", ""),
        "type": label.get("category", "Unknown"),
        "subject": label.get("subject", "Unknown"),
        "text": post.get("text", "")
    }
    labeled.append(post_out)
    with open(LABELED_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(labeled, f, ensure_ascii=False, indent=2)
    print(f"[DEBUG] Saved label for: {post_out.get('url') or post_out.get('text')[:30]}")

# ✅ تصنيف
def classify_post_text(text, idx):
    if not text.strip():
        print(f"[DEBUG][{idx}] Empty post, skipping…")
        return {"category": "Other", "subject": "Unknown"}

    body = {
        "contents": [
            {"parts": [{"text": f"Classify this Facebook post into JSON with keys category and subject:\n\n{text}"}]}
        ]
    }

    url = f"{GENIE_URL}?key={GOOGLE_API_KEY}"
    r = requests.post(url, headers=HEADERS, json=body)

    if r.status_code == 429:
        print(f"[DEBUG][{idx}] Rate limit, wait 30s…")
        time.sleep(30)
        return classify_post_text(text, idx)

    if r.status_code != 200:
        print(f"[DEBUG][{idx}] HTTP {r.status_code}: {r.text}")
        return {"category": "Error", "subject": "Error"}

    try:
        data = r.json()
        output_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"[DEBUG][{idx}] Output: {output_text}")
        return json.loads(output_text)
    except Exception as e:
        print(f"[DEBUG][{idx}] Failed to parse: {e}")
        return {"category": "Other", "subject": "Unknown"}

# ✅ Main
def main():
    posts = load_raw_posts()
    labeled = load_labeled_posts()
    done_urls = {item.get("url") for item in labeled}

    print(f"[DEBUG] Loaded {len(posts)} posts")

    for idx, post in enumerate(posts):
        if post.get("url") in done_urls:
            continue  # ✅ Skip done

        labels = classify_post_text(post.get("text", ""), idx)
        save_label(post, labels)
        time.sleep(RATE_LIMIT_DELAY)

    print("[INFO] Classification completed.")

if __name__ == "__main__":
    main()
