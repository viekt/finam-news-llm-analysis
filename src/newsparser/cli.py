import os
import argparse
from .parser import run
from dotenv import load_dotenv
from .config import WORK_FOLDER

def main():
    parser = argparse.ArgumentParser(
        description="FINAM news parser — полный pipeline"
    )
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='URL news source (for example, https://www.finam.ru/publications/section/companies/date/2023-11-01/2025-03-31/)'
    )
    parser.add_argument(
        '--output', '-o',
        default='df_news_total_info.xlsx',
        help='Name of file to save results (Excel with date,title,text,signal…)'
    )
    args = parser.parse_args()

    if WORK_FOLDER:
        os.makedirs(WORK_FOLDER, exist_ok=True)
        filename = os.path.basename(args.output)
        output_path = os.path.join(WORK_FOLDER, filename)
    else:
        output_path = args.output
    run(args.source, output_path)

if __name__ == '__main__':
    main()
