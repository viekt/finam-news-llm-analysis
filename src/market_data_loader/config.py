import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.txt")

EXTRA_FOLDER = os.getenv("EXTRA_FILES_FOLDER", "")
if EXTRA_FOLDER:
    os.makedirs(EXTRA_FOLDER, exist_ok=True)

DB_PATH = os.path.join(EXTRA_FOLDER, "market_data.db")
TICKERS_PKL = os.path.join(EXTRA_FOLDER, "tickers_extended.pkl")
