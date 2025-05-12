import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns

from .db import fetch_daily
from .utils import (
    trading_days_index,
    determine_trading_time,
)
from .config import INDEX_TICKER, TRADING_START, TRADING_END

class PortfolioReturn:
    def __init__(self, start, end):
        self.trading_days = trading_days_index(start, end)
    
    def separate(self, df: pd.DataFrame):
        df["date"] = pd.to_datetime(df["date"], format="%d.%m.%y %H:%M")
        df["trading_time"] = df["date"].apply(
            lambda dt: determine_trading_time(dt, self.trading_days)
        )
        return (
          df[df["trading_time"].isna()].copy(),
          df[df["trading_time"].notna()].copy()
        )
    

    def calculate_return(
        self,
        non_trading: pd.DataFrame,
        strategy: str = "gpt",
        include_index: bool = True,
        hour_open: int = 10,
        minute_open: int = 1,
        hour_close: int = 18,
        minute_close: int = 39,
        exclude_neutral: bool = True

    ) -> pd.DataFrame:
        """
        Applies a signal strategy, then computes excess returns and
        returns.
        """
        non_trading_df = non_trading.copy()

        if strategy == "all_long":
            non_trading_df["signal"] = 1
        elif strategy == "all_short":
            non_trading_df["signal"] = -1
        elif strategy == "random":
            non_trading_df["signal"] = np.random.choice([-1, 1, 0], size=len(non_trading_df))
        elif strategy == "gpt_short":
            non_trading_df = non_trading_df[non_trading_df["signal"] != 1]
        elif strategy == "gpt_long":
            non_trading_df = non_trading_df[non_trading_df["signal"] != -1]

        non_trading_df["trading_date"] = pd.to_datetime(non_trading_df["trading_date"])
        non_trading_df["trading_time"] = non_trading_df["trading_date"].apply(
            lambda d: d.replace(hour=hour_open, minute=minute_open)
        )

        results = []
        for _, row in non_trading_df.iterrows():
            ticker       = row["ticker"]
            trading_time = row["trading_time"]
            signal       = row["signal"]

            mkt = fetch_daily(
                ticker,
                trading_time,
                trading_time.replace(hour=hour_close, minute=minute_close),
            )
            idx = fetch_daily(
                INDEX_TICKER,
                trading_time,
                trading_time.replace(hour=hour_close, minute=minute_close),
            )

            if mkt.empty:
                continue

            entry_price = mkt.open.iloc[0]
            exit_price  = mkt.close.iloc[0]
            entry_idx   = idx.open.iloc[0]
            exit_idx    = idx.close.iloc[0]

            if signal == 1:
                trade_ret = (exit_price - entry_price) / entry_price 
            else:
                trade_ret = (entry_price - exit_price) / entry_price

            if include_index:
                idx_ret = (exit_idx - entry_idx) / entry_idx if signal == 1 else (entry_idx - exit_idx) / entry_idx
            else:
                idx_ret = 0

            # filter out zeros or IMOEX
            if ticker == INDEX_TICKER:
                continue
            if signal == 0 and exclude_neutral:
                continue

            results.append({
                "time": trading_time,
                "ticker": ticker,
                "return": trade_ret - idx_ret,
                "signal": signal,
                "combined_prompt": row["combined_prompt"],
                "explanation": row["explanation"],
                "news_time": row["trading_date"],
            })

        return pd.DataFrame(results)
    
    def create_df_regression(
        self,
        non_trading: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        For each row in non_trading, fetch market data between fixed times
        (10:01 to 18:39) and compute raw, index, and excess returns.
        Returns a DataFrame with columns:
          ['time','ticker','raw_return','index_return','excess_return','news_time']
        """
        df = non_trading.copy()
        df["trading_date"] = pd.to_datetime(df["trading_date"])

        open_hour, open_min = 10, 1
        close_hour, close_min = 18, 39

        df["trading_time"] = df["trading_date"].apply(
            lambda d: d.replace(hour=open_hour, minute=open_min)
        )

        results = []
        for _, row in df.iterrows():
            ticker = row["ticker"]
            time_open = row["trading_time"]
            time_close = time_open.replace(hour=close_hour, minute=close_min)

            mkt = fetch_daily(ticker, time_open, time_close)
            if mkt.empty:
                continue

            entry_price, exit_price = mkt.open.iloc[0], mkt.close.iloc[0]
            raw_ret = (exit_price - entry_price) / entry_price

            idx = fetch_daily(INDEX_TICKER, time_open, time_close)
            if idx.empty:
                continue
            else:
                index_entry_price, index_exit_price = idx.open.iloc[0], idx.close.iloc[0]
                idx_ret = (index_exit_price - index_entry_price) / index_entry_price


            results.append({
                "ticker": ticker,
                "signal": row["signal"],
                "raw_return":    raw_ret,
                "index_return":  idx_ret,
                "excess_return": raw_ret - idx_ret,
                "trading_date":     row["trading_date"],
            })

        return pd.DataFrame(results)
    
    def _compute_metrics(self, returns: pd.Series) -> dict:
        """
        Given a Series of daily returns, compute
        mean, std, Sharpe (annualized), and max drawdown.
        """
        mean_ret = returns.mean()
        std_ret  = returns.std()
        sharpe   = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else np.nan

        cum = (1 + returns).cumprod()
        peak = cum.cummax()
        drawdown = (cum - peak) / peak
        max_dd = drawdown.min()

        return {
            "sharpe_ratio": sharpe,
            "mean_return_daily_pct": mean_ret * 100,
            "std_daily_pct": std_ret * 100,
            "max_drawdown_pct": max_dd * 100
        }

    def calculate_cumulative_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        1) Group by news_time, compute avg return
        2) Compute cumulative return
        3) Attach Sharpe, mean, std, drawdown (as %)
        """
        dfg = (df.groupby("news_time")['return'].mean().rename("avg_return").reset_index().sort_values("news_time"))
        
        dfg["multiplier"] = 1 + dfg["avg_return"]
        dfg["cumulative_return"] = dfg["multiplier"].cumprod()

        metrics = self._compute_metrics(dfg["avg_return"])
        for k, v in metrics.items():
            dfg[k] = v

        return dfg

    def calculate_self_financing_cum_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        1) Split long vs short signals and average per day
        2) Sum into daily_ret, cumprod into cumulative_return
        3) Attach Sharpe, mean, std, drawdown (as %)
        """
        long_r = (df[df.signal == 1].groupby("news_time")['return'].mean().rename("long_ret"))
        short_r = (df[df.signal == -1].groupby("news_time")['return'].mean().rename("short_ret"))

        pr = pd.concat([long_r, short_r], axis=1).fillna(0)
        pr["daily_ret"] = pr["long_ret"] + pr["short_ret"]
        pr = pr.sort_index()
        pr["cumulative_return"] = (1 + pr["daily_ret"]).cumprod()

        metrics = self._compute_metrics(pr["daily_ret"])
        for k, v in metrics.items():
            pr[k] = v

        return pr.reset_index()
    
    def estimate_random_benchmark(
        self,
        non_trading_df: pd.DataFrame,
        n_runs: int = 100,
        include_index: bool = False,
        hour_open: int = 10,
        minute_open: int = 1,
        hour_close: int = 18,
        minute_close: int = 39,
        seed_offset: int = 0,
    ) -> tuple[pd.Series, dict]:
        """
        Run `n_runs` of the random‐signal strategy, each time computing the
        self‐financing cumulative return series, then:
          1) returns a Series of the MEAN cumulative return over time,
          2) returns a dict of average metrics (Sharpe, mean%, std%, max DD%).
        """

        cum_returns = []
        metrics_list = []

        for i in range(n_runs):
            np.random.seed(i + seed_offset)
            df_rand = self.calculate_return(
                non_trading_df,
                strategy="random",
                include_index=include_index,
                hour_open=hour_open,
                minute_open=minute_open,
                hour_close=hour_close,
                minute_close=minute_close,
            )


            result = self.calculate_self_financing_cum_return(df_rand)
            cr = result.set_index("news_time")["cumulative_return"]
            cum_returns.append(cr)
            metrics_list.append({
                "Sharpe (Annualized)":       result["sharpe_ratio"].iloc[0],
                "Mean Daily Return (%)":     result["mean_return_daily_pct"].iloc[0],
                "Std. Dev. (%)":             result["std_daily_pct"].iloc[0],
                "Max Drawdown (%)":          result["max_drawdown_pct"].iloc[0],
            })

        cum_df = pd.concat(cum_returns, axis=1).sort_index()
        cum_df.columns = [f"run_{i}" for i in range(n_runs)]

        mean_cum_return = cum_df.mean(axis=1)

        metrics_df = pd.DataFrame(metrics_list)
        avg_metrics = metrics_df.mean(numeric_only=True).to_dict()

        return mean_cum_return, avg_metrics
    

    def plot_with_random(
        self,
        portfolios: dict[str, pd.DataFrame],
        mean_random: pd.Series,
        random_metrics: dict[str, float],
        output_prefix: str = "fig_cumulative_returns_raw",
        title: str = "Cumulative Returns by Strategy\n(Open 10-min / Close 10-min)"
    ) -> dict[str, dict]:
        """
        portfolios: {
          label -> DataFrame with at least ['news_time','return','signal']
        }
        mean_random: pd.Series indexed by news_time of expected-random cum. return
        random_metrics: dict with keys
          'Sharpe (Annualized)', 'Mean Daily Return (%)', 'Std. Dev. (%)', 'Max Drawdown (%)'
        """
        sns.set_style("whitegrid")
        plt.figure(figsize=(12, 6), dpi=300)
        plt.rcParams.update({
            "text.usetex": False,
            "font.family": "serif",
            "axes.labelsize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 12
        })

        colors = ['red', 'green', 'orange', 'purple', 'brown', 'pink']
        metrics: dict[str, dict] = {}

        for (label, df), color in zip(portfolios.items(), colors):
            if df.empty:
                continue

            if label in {"GPT", "Only long GPT", "Only short GPT", "Random"}:
                res = self.calculate_self_financing_cum_return(df)
                ls = "dashed"
            else:
                res = self.calculate_cumulative_return(df)
                ls = "solid"

            plt.plot(
                res["news_time"],
                res["cumulative_return"],
                label=label,
                color=color,
                linestyle=ls
            )

            metrics[label] = {
                "Sharpe (Annualized)"   : res["sharpe_ratio"].iloc[0],
                "Mean Daily Return (%)" : res["mean_return_daily_pct"].iloc[0],
                "Std. Dev. (%)"         : res["std_daily_pct"].iloc[0],
                "Max Drawdown (%)"      : res["max_drawdown_pct"].iloc[0],
            }

        plt.plot(
            mean_random.index,
            mean_random.values,
            label="Expected Random",
            color="black",
            linestyle="dotted"
        )
        metrics["Expected Random"] = random_metrics

        plt.title(title)
        plt.xlabel("Date")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(f"{output_prefix}.pgf")
        plt.savefig(f"{output_prefix}.png")
        plt.show()

        return metrics
    
