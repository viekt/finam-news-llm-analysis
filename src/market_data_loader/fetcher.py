# src/market_data_loader/fetcher.py
import asyncio
import pickle
from datetime import date
import pandas as pd
from moexalgo import Ticker, Index
from .db import get_conn, init_db
from .config import TICKERS_PKL
import logging

logger = logging.getLogger(__name__)

async def fetch_one(ticker: str, day: date, period: int = 1):
    cls = Index if ticker == "IMOEX" else Ticker
    inst = cls(ticker)
    df = await asyncio.to_thread(
        lambda: inst.candles(start=str(day), end=str(day), period=period)
    )
    if df is None or "begin" not in df.columns:
        return []
    df["begin"] = pd.to_datetime(df["begin"])
    rows = [
        (
            ticker,
            row.begin.strftime("%Y-%m-%d %H:%M:%S"),
            float(row.open),
            float(row.high),
            float(row.low),
            float(row.close),
            float(row.volume),
        )
        for row in df.itertuples()
    ]
    return rows

async def update_all(trading_days: list[date], period: int):
    # load your tickers from pickle
    with open(TICKERS_PKL, "rb") as f:
        tickers = pickle.load(f)

    # ensure table exists
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    for ticker in tickers:
        total_rows = 0
        for day in trading_days:
            rows = await fetch_one(ticker, day, period)
            if not rows:
                continue
            cur.executemany(
                '''INSERT OR IGNORE INTO ticker_data
                   (ticker, date, open, high, low, close, volume)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                rows
            )
            total_rows += len(rows)
        logger.info("Inserted %d rows for %s", total_rows, ticker)
    conn.close()
    logger.info("All tickers updated")
