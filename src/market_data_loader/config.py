import os

DB_PATH = os.getenv("MARKET_DB_PATH", "market_data.db")
TICKERS_PKL = os.getenv("TICKERS_PKL", "tickers_extended.pkl")
