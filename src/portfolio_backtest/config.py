import os

# path to your SQLite store
DB_PATH = os.getenv("MARKET_DB_PATH", "market_data.db")

# IMOEX index ticker for reference
INDEX_TICKER = "IMOEX"

# Trading window boundaries
TRADING_START = "09:51:00"
TRADING_END   = "18:49:00"
