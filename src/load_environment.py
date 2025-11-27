import os

from dotenv import load_dotenv

# === Load environment variables ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Prioridad: .env.local → .env
dotenv_path = os.path.join(BASE_DIR, "..", ".env.local")
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(BASE_DIR, "..", ".env")

print(f"📂 Loading environment from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)
