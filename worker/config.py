import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
DATA_DIR = BASE_DIR / 'data'
CACHE_DIR = BASE_DIR / 'cache'

load_dotenv(ENV_PATH)

ZENO_SERVER = os.getenv('ZENO_SERVER', '').strip()
ZENO_PORT = os.getenv('ZENO_PORT', '80').strip()
ZENO_MOUNT = os.getenv('ZENO_MOUNT', '').strip()
ZENO_USERNAME = os.getenv('ZENO_USERNAME', 'source').strip()
ZENO_PASSWORD = os.getenv('ZENO_PASSWORD', '').strip()

QUEUE_PATH = str(DATA_DIR / 'queue.json')
LIB_PATH = str(DATA_DIR / 'library.json')
STATE_PATH = str(DATA_DIR / 'state.json')
CONTROL_PATH = str(DATA_DIR / 'control.json')
CACHE_INDEX_PATH = str(DATA_DIR / 'cache_index.json')
HISTORY_PATH = str(DATA_DIR / 'history.json')
