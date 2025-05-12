import argparse
import pandas as pd
from .portfolio import PortfolioReturn

def main():
    p = argparse.ArgumentParser(
        description="Compute news‑driven excess returns"
    )
    p.add_argument("--input","-i", required=True,
                   help="Excel with date,title,text,signal…")
    p.add_argument("--output","-o", default="returns.xlsx",
                   help="Where to save results")
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end",   required=True, help="YYYY-MM-DD")
    args = p.parse_args()

    df = pd.read_excel(args.input)
    pr = PortfolioReturn(args.start, args.end)
    trading, non_trading = pr.separate(df)
    # choose which df to pass in, or concat
    res = pr.batch_returns(pd.concat([trading, non_trading]), strategy="gpt")
    res.to_excel(args.output, index=False)

if __name__=="__main__":
    main()
