import argparse
from datetime import date, timedelta
import asyncio
import logging
from .fetcher import update_all

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s │ %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def main():
    p = argparse.ArgumentParser(
        description="Fill or update local market_data.db from MOEX"
    )
    p.add_argument(
        "--start", "-s",
        required=True,
        help="Start date, YYYY-MM-DD"
    )
    p.add_argument(
        "--end", "-e",
        required=True,
        help="End date, YYYY-MM-DD"
    )
    p.add_argument(
        "--period", "-p",
        type=int,
        default=1,
        help="MOEX candle period (1=daily)"
    )
    args = p.parse_args()

    start = date.fromisoformat(args.start)
    end   = date.fromisoformat(args.end)
    days = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += timedelta(days=1)
    logger.info(
        "Will fetch from %s to %s (period=%d)",
        args.start, args.end, args.period
    )

    asyncio.run(update_all(days, args.period))
    logger.info("Finished updating market_data.db")

if __name__ == "__main__":
    main()
