# Module for thesis on LLM usage for financial news analysis
## Project Overview

finam-news-llm-analysis is a toolkit and pipeline for ingesting, processing, and analyzing financial news using large language models (LLMs) and traditional market-data sources. It provides:
Automated news parsing from raw feeds or web sources.
LLM-based labeling and sentiment analysis via OpenAI’s ChatGPT API.
Market data loading to augment textual insights with price and volume context.
Reproducible analysis pipelines in Jupyter notebooks. 

## Key Features

Command-line interfaces for each major task (news-parser, chatgpt-news-label, market-load) through console_scripts entry points 
Modular Python package (finance_toolkit) installable via setup.py 
Notebook-driven pipeline (analysis_pipeline.ipynb) showcasing end-to-end ingestion, processing, LLM labeling, and visualization 
Plots directory containing example visual outputs 
Work files and extra files for intermediate artifacts and reference data 
