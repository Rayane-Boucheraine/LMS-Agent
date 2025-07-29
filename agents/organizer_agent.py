import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from config.config import LABELED_POSTS_FILE, GOOGLE_CREDENTIALS_PATH

# إعداد Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_PATH, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=creds)

# إنشاء فولدر في Google Drive
def create_folder(name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    if results["files"]:
        return results["files"][0]["id"]

    file_metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        file_metadata["parents"] = [parent_id]
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")

# رفع ملف JSON
def upload_json(name, content, folder_id):
    file_metadata = {"name": name, "parents": [folder_id], "mimeType": "application/json"}
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="application/json")
    drive_service.files().create(body=file_metadata, media_body=media).execute()

def main():
    if not os.path.exists(LABELED_POSTS_FILE):
        print("[ERROR] labeled_posts.json not found")
        return

    with open(LABELED_POSTS_FILE, "r") as f:
        posts = json.load(f)

    if not posts:
        print("[INFO] No posts to organize")
        return

    # إنشاء مجلد رئيسي ومجلدات فرعية
    root_id = create_folder("LMS Organized Data")
    courses_id = create_folder("Courses", root_id)
    exams_id = create_folder("Exams", root_id)
    others_id = create_folder("Other", root_id)

    # تصنيف البوستات
    courses = [p for p in posts if p["type"] == "Course"]
    exams = [p for p in posts if p["type"] == "Exam"]
    others = [p for p in posts if p["type"] not in ["Course", "Exam"]]

    # رفع الملفات
    upload_json("courses.json", json.dumps(courses, indent=2, ensure_ascii=False), courses_id)
    upload_json("exams.json", json.dumps(exams, indent=2, ensure_ascii=False), exams_id)
    upload_json("others.json", json.dumps(others, indent=2, ensure_ascii=False), others_id)

    print("[INFO] Data organized and uploaded to Google Drive")

if __name__ == "__main__":
    main()
