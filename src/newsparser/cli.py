import argparse
from .parser import run

def main():
    parser = argparse.ArgumentParser(
        description="MOEX publications parser — полный pipeline"
    )
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='URL секции (…/section/…) или путь/URL к JSON'
    )
    parser.add_argument(
        '--output', '-o',
        default='df_news_total_info.xlsx',
        help='Куда сохранить итоговый Excel'
    )
    args = parser.parse_args()
    run(args.source, args.output)

if __name__ == '__main__':
    main()
