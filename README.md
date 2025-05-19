# Module for thesis on LLM usage for financial news analysis
## Project Overview

finam-news-llm-analysis is a toolkit and pipeline for ingesting, processing, and analyzing financial news using large language models (LLMs) and traditional market-data sources. It provides:
- Automated news parsing from raw feeds or web sources.
- LLM-based labeling and sentiment analysis via OpenAI’s ChatGPT API.
- Market data loading to augment textual insights with price and volume context.
- Reproducible analysis pipelines in Jupyter notebooks. 

## Key Features

- Command-line interfaces for each major task (news-parser, chatgpt-news-label, market-load) through console_scripts entry points 
- Modular Python package (finance_toolkit) installable via setup.py 
- Notebook-driven pipeline (analysis_pipeline.ipynb) showcasing end-to-end ingestion, processing, LLM labeling, and visualization 
- Plots directory containing example visual outputs 
- Work files and extra files for intermediate artifacts and reference data 


## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/viekt/finam-news-llm-analysis.git
   cd finam-news-llm-analysis
   ```
2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -e
   ```

## Commands to prepare all necessary files to work with
1. Parse raw news
```bash
news-parser \
  --input https://www.finam.ru/publications/section/companies/date/2023-11-01/2025-03-31/ \
  --output parsed_news.csv
```
3. Label with ChatGPT
```bash
chatgpt-news-label \
  --input parsed_news.csv \
  --output labeled_news.csv
```
5. Load market data
```bash
market-load \
  --start 2025-01-01 \
  --end   2025-05-19 \
  --period 1
```

## Project Structure

finam-news-llm-analysis/
├── extra_files/                # Reference datasets (lookup tables, mappings)
├── plots/                      # Sample visualization outputs (PNG, SVG)
├── src/                        # Top-level Python package
│   ├── newsparser/             # `news-parser` CLI & modules
│   │   └── cli.py
│   ├── chatgpt_news_label/     # `chatgpt-news-label` CLI & modules
│   │   └── cli.py
│   └── market_data_loader/     # `market-load` CLI & modules
│       └── cli.py
├── work_files/                 # Scratch & intermediate files
├── analysis_pipeline.ipynb     # End-to-end Jupyter notebook demo
├── setup.py                    # Installation & console_scripts entry points
├── .gitignore                  # Git ignore rules
└── README.md                   # Project README (this file)


