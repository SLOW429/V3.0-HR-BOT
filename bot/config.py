import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
ROOM_ID = os.getenv('ROOM_ID', '').strip()
OWNER_USERNAME = os.getenv('OWNER_USERNAME', '').strip().lower()
