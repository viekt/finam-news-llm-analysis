import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.txt")

EXTRA_FOLDER = os.getenv("EXTRA_FILES_FOLDER", "")

if EXTRA_FOLDER:
    os.makedirs(EXTRA_FOLDER, exist_ok=True)

# path to your SQLite store
DB_PATH = os.path.join(EXTRA_FOLDER, "market_data.db")

# IMOEX index ticker for reference
INDEX_TICKER = "IMOEX"

# Trading window boundaries
TRADING_START = "09:51:00"
TRADING_END   = "18:49:00"
