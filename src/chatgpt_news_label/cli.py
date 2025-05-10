import argparse
from .chatgpt_label import run

def main():
    parser = argparse.ArgumentParser(
        description="Label financial news via ChatGPT API"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to non_trading_df_total_info.xlsx"
    )
    parser.add_argument(
        "--output", "-o",
        default="gpt_signals.json",
        help="Where to save the JSON with signals"
    )
    parser.add_argument(
        "--model", "-m",
        default="gpt-4o-2024-08-06",
        help="OpenAI model to use"
    )
    args = parser.parse_args()
    run(args.input, args.output, model=args.model)

if __name__ == "__main__":
    main()
