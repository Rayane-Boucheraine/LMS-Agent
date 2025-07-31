import json
import os
import re
import time
from collections import defaultdict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.errors import HttpError
from config.config import LABELED_POSTS_FILE, GOOGLE_CREDENTIALS_PATH, SHARED_DRIVE_ID

# 1️⃣ Google Drive API setup
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_PATH, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=creds)

# 2️⃣ Folder groups for regrouping
FOLDER_GROUPS = {
    "Study": [
        "Study Materials", "Study Material", "Study Resources",
        "Study Aid", "Study Help", "Study Notes", "Notes",
        "Study/Summary", "Study/School", "Study Skills",
        "Study Guides & Summaries", "Study Guides/Summaries"
    ],
    "Summaries": [
        "Summaries", "Summary", "Résumé",
        "Study Notes/Summary", "Study Materials/Summary",
        "Study Materials/Summaries", "Study Skills/Summarization",
        "Study Aid/Summary", "Summaries/Note-Taking", "Summaries/Notes",
        "Study Skills/Note Taking/Summarization"
    ],
    "Medicine": [
        "Medicine", "Medical Studies", "Medical School",
        "Healthcare Documentation", "Medical Residency",
        "Medical Residency Exam Preparation", "Medical Residency Exams",
        "Medical Residency Preparation", "Medical Residency Entrance Exam Preparation",
        "Medical Residency Exam Preparation (Ophthalmology)",
        "Medicine (Specifically Endocrinology And Diabetology Residency Exam Preparation)",
        "Medicine (UMC)"
    ],
    "Biology": [
        "Biology", "Histology", "Cell Biology",
        "Anatomy", "Physiology", "Neuroscience", "Hematology",
        "Biochemistry", "Pathology", "Cellular Pathology", "Anatomy And Pathology"
    ],
    "Cardiology": [
        "Cardiology", "Electrocardiography", "Electrocardiography (Ecg)",
        "Tachycardia", "Hemorrhage And Hemorrhagic Shock", "Atherosclerosis"
    ],
    "Pulmonology": [
        "Pulmonology", "Respiratory Medicine", "Pulmonary Examination",
        "Respiratory Sounds", "Acute Respiratory Distress Syndrome", "Snoring"
    ],
    "Psychiatry": ["Psychiatry"],
    "Pediatrics": ["Pediatrics"],
    "Urology": ["Urology"],
    "Islamic Studies": ["Islamic Studies/Guidance/Exam Preparation"],
    "Economics": ["Economics"],
    "French Language": ["French Language"],
    "Career Advice": ["Career Advice"],
    "Exams": ["Exams"],
    "Mathematics": ["Mathematics"],
    "Diabetes": [
        "Diabetes", "Diabète Type 1", "Diabète Type 2",
        "Comparaison Entre Le Diabète De Type 1 Et Le Diabète De Type 2",
        "Définition Et Classification Du Diabète Sucré"
    ],
    "Immunology": ["Immunology"],
    "Neurology": ["Neurology", "Intracranial Hypertension", "Hydrocéphalie"],
    "Radiology": ["Radiology"],
    "Resume": ["Resume", "Resume Writing"],
    "Youtube Milestone": ["Youtube Milestone"],
}

# 3️⃣ Normalize subject names
def normalize_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip()).title()

# 4️⃣ Create HTML body with clickable links
def build_html_body(videos):
    html = "<!DOCTYPE html><html><body><h2>Videos</h2><ul>"
    for v in videos:
        url = v.get("url", "#")
        title = v.get("title", url)
        html += f'<li><a href="{url}" target="_blank">{title}</a></li>'
    html += "</ul></body></html>"
    return html

# 5️⃣ Get or create folder in Shared Drive
def get_or_create_folder(name, parent_id):
    q = (
        f"name='{name}' and '{parent_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    res = drive_service.files().list(
        q=q,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        fields="files(id)"
    ).execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = drive_service.files().create(
        body=metadata,
        supportsAllDrives=True,
        fields="id"
    ).execute()
    return folder["id"]

# 6️⃣ Upload Google Doc with retry for 500 errors
def upload_doc(name, html_content, folder_id):
    media = MediaInMemoryUpload(html_content.encode("utf-8"), mimetype="text/html")
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id]
    }

    for attempt in range(5):
        try:
            drive_service.files().create(
                body=metadata,
                media_body=media,
                supportsAllDrives=True,
                fields="id"
            ).execute()
            return
        except HttpError as e:
            if e.resp.status == 500:
                wait_time = 2 ** attempt
                print(f"[WARN] Google Drive 500 error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

def main():
    if not os.path.exists(LABELED_POSTS_FILE):
        print(f"[ERROR] File not found: {LABELED_POSTS_FILE}")
        return

    with open(LABELED_POSTS_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)
    if not posts:
        print("[INFO] No posts to process")
        return

    grouped = defaultdict(list)
    for p in posts:
        subj_raw = normalize_text(p.get("subject", ""))
        main_folder = None
        for mf, variants in FOLDER_GROUPS.items():
            if subj_raw in variants:
                main_folder = mf
                break
        if not main_folder:
            main_folder = subj_raw
        grouped[(main_folder, subj_raw)].append(p)

    root_id = SHARED_DRIVE_ID

    for (main_folder, subj), vids in grouped.items():
        folder_id = get_or_create_folder(main_folder, root_id)
        doc_name = f"{subj}.doc"
        html = build_html_body(vids)
        upload_doc(doc_name, html, folder_id)
        print(f"[INFO] Uploaded {len(vids)} videos as Doc '{main_folder}/{doc_name}'")
        time.sleep(0.5)  # small delay to avoid rate limit

    print("[INFO] ✅ All organized and uploaded!")

if __name__ == "__main__":
    main()
