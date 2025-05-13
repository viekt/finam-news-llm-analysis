import argparse
from dotenv import load_dotenv

from .chatgpt_label import run

load_dotenv(dotenv_path=".env.txt")
WORK_FOLDER = os.getenv("WORK_FILES_FOLDER", "")
if WORK_FOLDER:
    import os
    os.makedirs(WORK_FOLDER, exist_ok=True)
    
def main():
    parser = argparse.ArgumentParser(
        description="Label financial news via ChatGPT API"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to dataset with news to label (Excel with date,title,text,signal…)"
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
    if WORK_FOLDER: 
        input_path = os.path.join(WORK_FOLDER, os.path.basename(args.input))
        output_path = os.path.join(WORK_FOLDER, os.path.basename(args.output))
    else:
        input_path = args.input
        output_path = args.output
    run(input_path, output_path, model=args.model)

if __name__ == "__main__":
    main()
