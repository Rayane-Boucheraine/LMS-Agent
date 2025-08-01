import subprocess
import sys
import os
from config.config import LABELED_POSTS_FILE

def run_module(module_name):
    print(f"[INFO] Running {module_name} ...")
    result = subprocess.run([sys.executable, "-m", module_name])
    if result.returncode != 0:
        print(f"[ERROR] {module_name} failed!")
        sys.exit(1)

def main():
    # 1️⃣ Run Scraper Agent first (optional)
    run_module("agents.scraper_agent")

    # 2️⃣ Run Labeling Agent
    run_module("agents.labeling_agent")

    # 3️⃣ Ensure labeling created the file
    if not os.path.exists(LABELED_POSTS_FILE):
        print("[ERROR] labeled_posts.json not found, skipping organizing agent.")
        sys.exit(1)

    # 4️⃣ Run Organizer Agent
    run_module("agents.organizer_agent")

    print("[INFO] ✅ Pipeline completed successfully!")

if __name__ == "__main__":
    main()