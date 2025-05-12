import pandas as pd
from datetime import timedelta
from .config import TRADING_START, TRADING_END

def trading_days_index(start, end):
    """
    Return a DatetimeIndex of IMOEX trading days (24h candles).
    """
    from moexalgo import Index
    return Index("IMOEX").candles(start=start, end=end, period=24)["begin"]

def find_next_trading_day(days: pd.DatetimeIndex, dt: pd.Timestamp):
    return days[days.dt.date > dt.date()].iloc[0]

def find_closest_or_next(days: pd.DatetimeIndex, dt: pd.Timestamp):
    future = days[days.dt.date >= dt.date()]
    return future.iloc[0]

def determine_trading_time(dt: pd.Timestamp, trading_days: pd.DatetimeIndex):
    start = pd.to_datetime(f"{dt.date()} {TRADING_START}")
    end   = pd.to_datetime(f"{dt.date()} {TRADING_END}")

    # before open → assign to that day's start
    if dt < start:
        cand = start
    # after close → next day's open
    elif dt > end:
        cand = start + timedelta(days=1)
    # during trading hours → nothing to shift
    else:
        return None

    # if cand isn’t a trading day, bump to the next one
    if cand.date() not in set(trading_days.dt.date):
        cand = find_closest_or_next(trading_days, cand)

    return cand
