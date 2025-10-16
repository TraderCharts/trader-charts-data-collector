# config.py
"""
Configuration file for the Selenium CSV Downloader project.
Recommended structure for Python scripts, libraries, and microservices.
"""

from dotenv import load_dotenv
import os

# === Load environment variables ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Prioridad: .env.local → .env
dotenv_path = os.path.join(BASE_DIR, "..", ".env.local")
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(BASE_DIR, "..", ".env")

print(f"📂 Loading environment from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)


# === General settings ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory where CSVs will be downloaded
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(BASE_DIR, "downloads"))

# === Selenium settings ===
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", 20))
CHROME_WINDOW_SIZE = os.getenv("CHROME_WINDOW_SIZE", "1920,1080")
SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "True").lower() == "true"

# === MongoDB settings (sensitive information) ===
# Must be set in the environment or in .env.local; do not hardcode
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

