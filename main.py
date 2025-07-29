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
    # 1️⃣ تشغيل Labeling Agent
    run_module("agents.labeling_agent")

    # 2️⃣ التأكد من أن labeling نجح وأن الملف موجود
    if not os.path.exists(LABELED_POSTS_FILE):
        print("[ERROR] labeled_posts.json not found, skipping organizing agent.")
        sys.exit(1)

    # 3️⃣ تشغيل Organizing Agent
    run_module("agents.organize_agent")

    print("[INFO] ✅ Pipeline completed successfully!")

if __name__ == "__main__":
    main()
