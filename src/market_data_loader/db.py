# src/market_data_loader/db.py
import sqlite3
from .config import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)

def init_db():
    c = get_conn().cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ticker_data (
            ticker TEXT,
            date   DATETIME,
            open   REAL,
            high   REAL,
            low    REAL,
            close  REAL,
            volume REAL,
            PRIMARY KEY (ticker, date)
        )
    ''')
