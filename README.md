# 📚 LMS Agent - YouTube Courses Scraper

## 📌 Overview
This project uses intelligent agents to scrape **courses and exams from YouTube playlists/channels** and automatically organize them into Google Drive folders based on video titles and descriptions.

## ✅ Features:
- Fetches data from **YouTube API** or direct video links.
- Classifies videos into categories (Courses / Exams / Notes / Study Materials).
- Stores and organizes files automatically in Google Drive.
- Full pipeline: **Scraper → Labeling → Organizer**.
- Auto-updates every 6 hours without manual intervention.

## 📂 Project Structure:
```
LMS-Agent/
│
├── data/                     # Local data storage
│   ├── raw_videos.json
│   ├── new_videos.json
│   ├── labeled_videos.json
│   └── last_update.txt
│
├── agents/                   # Project Agents
│   ├── scraper_agent.py      # Fetch videos from YouTube
│   ├── labeling_agent.py     # Classify videos into subjects
│   └── organizer_agent.py    # Upload and organize in Google Drive
│
├── config/
│   ├── config.py             # API Keys and settings
│   └── credentials.json      # Google API credentials
│
├── main.py                   # Main file to run all agents
├── requirements.txt          # Project dependencies
└── README.md
```

## 🔧 Installation:
```bash
git clone <repo_url>
cd LMS-Agent
pip install -r requirements.txt
```

## 🚀 Usage:
```bash
python main.py
```

## 🛠️ Setup:
1. Add your **YouTube API key** and channel/playlist IDs in `config/config.py`.
2. Add your Google API credentials JSON in `config/credentials.json`.
3. Use a Cron Job or Python Scheduler to run `main.py` every 6 hours for automatic updates.

## 📌 Tools & Technologies:
* YouTube API
* CrewAI
* Google Drive API
* Python 3.11+