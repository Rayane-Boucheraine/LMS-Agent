# 📚 LMS Agent - Facebook Groups Scraper

## 📌 Overview
This project uses intelligent agents to scrape courses and exams from private Facebook student groups and automatically organize them into folders based on post descriptions and comments.

## ✅ Features:
- Fetches data from **Apify API** periodically.
- Classifies posts into categories (Courses / Exams / Notes).
- Stores and organizes files automatically in Google Drive.
- Auto-updates every 6 hours without manual intervention.

## 📂 Project Structure:
```
LMS-Agent/
│
├── data/                    # Local data storage
│   ├── raw_posts.json
│   ├── new_posts.json
│   ├── labeled_posts.json
│   └── last_update.txt
│
├── agents/                  # Project Agents
│   ├── scraper_agent.py
│   ├── labeling_agent.py
│   └── organizer_agent.py
│
├── config/
│   ├── config.py           # API Keys and settings
│   └── credentials.json    # Google API credentials
│
├── main.py                 # Main file to run all agents
├── requirements.txt        # Project dependencies
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
1. Add your Apify API Token and Dataset ID in `config/config.py`.
2. Add your Google API credentials JSON in `config/credentials.json`.
3. Use a Cron Job or Python Scheduler to run `main.py` every 6 hours for automatic updates.

## 📌 Tools & Technologies:
- Apify
- CrewAI
- Google SDK
- Python 3.11+