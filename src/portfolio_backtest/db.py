import sqlite3
import pandas as pd
from .config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    return conn

def fetch_daily(ticker: str, start_dt: pd.Timestamp, end_dt: pd.Timestamp) -> pd.DataFrame:
    """
    Returns a DataFrame of one OHLC bar per calendar date,
    taking first 'open' and last 'close' within the window.
    """
    sql = """
        SELECT date, open, close
        FROM ticker_data
        WHERE ticker=? AND date BETWEEN ? AND ?
        ORDER BY date
    """
    df = pd.read_sql(sql, get_conn(),
                     params=(ticker,
                             start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                             end_dt.strftime("%Y-%m-%d %H:%M:%S")))
    df["date"] = pd.to_datetime(df["date"])
    daily = (
        df.groupby(df["date"].dt.date)
          .agg(open = ("open","first"),
               close= ("close","last"))
          .reset_index()
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily
