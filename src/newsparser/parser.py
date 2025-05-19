import json
import threading
import asyncio
import re
import pandas as pd
import requests
import os

from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from moexalgo import Market
from .config import get_chrome_options, EXTRA_FILES_FOLDER

thread_local = threading.local()

def fetch_section(section_url: str):
    """
    Function to fetch articles from a given section URL.
    It loads the page, clicks the "Download more" button until no more articles are available,
    and then scrapes the titles and links of the articles.
    It returns two lists: one with titles and links, and another with short information about the articles.
    """
    options = get_chrome_options()
    driver = webdriver.Chrome(options=options)
    driver.get(section_url)  
    wait = WebDriverWait(driver, 3)

    article_available_short_info = []
    titles_with_links = []

    while True:
        try:
            overlay = driver.find_elements(By.CSS_SELECTOR, "div[data-part='menu-item']")
            if overlay:
                driver.execute_script("arguments[0].style.display = 'none';", overlay[0])

            load_more = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[@data-id='button-more']")
            ))
            driver.execute_script("arguments[0].click();", load_more)
            print("Button 'Download more' clicked")
        except Exception:
            print("Button 'Download more' not found or no more articles to load.")
            break

    # Scraping titles and links
    for el in driver.find_elements(By.CLASS_NAME, "cl-blue.font-l.bold"):
        titles_with_links.append({"title": el.text, "link": el.get_attribute("href")})
    for el in driver.find_elements(By.CLASS_NAME, "mb2x"):
        article_available_short_info.append(el.text.split('\n'))

    driver.quit()

    df_links = pd.DataFrame(titles_with_links)
    unique_titles = df_links[df_links['title'] != ''] \
        .drop_duplicates(subset='title') \
        .to_dict(orient='records')
    unique_short = [list(x) for x in set(tuple(l) for l in article_available_short_info)]

    path_unique_titles = os.path.join(EXTRA_FILES_FOLDER, 'titles_links_main.json')
    path_unique_short = os.path.join(EXTRA_FILES_FOLDER, 'article_short_info_main.json')
    with open(path_unique_titles, 'w', encoding='utf-8') as f:
        json.dump(unique_titles, f, ensure_ascii=False, indent=4)
    with open(path_unique_short, 'w', encoding='utf-8') as f:
        json.dump(unique_short, f, ensure_ascii=False, indent=4)

    return unique_titles, unique_short

def get_driver():
    """
    Thread‑local WebDriver.
    """
    if not hasattr(thread_local, 'driver'):
        thread_local.driver = webdriver.Chrome(options=get_chrome_options())
    return thread_local.driver

def get_data(title, link):
    """
    Function to scrape data from a given article link.
    It uses Selenium to load the page and extract the date and text of the article.
    """
    driver = get_driver()
    driver.get(link)
    try:
        date = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-id='date']"))
        ).text
        text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id='text']"))
        ).text
    except Exception as e:
        print(f"Error: {e}")
        date, text = None, ""
    finally:
        driver.quit()
        del thread_local.driver
    return {"title": title, "link": link, "date": date, "text": text}

async def scrape_all(titles_links):
    """
    Scrape all articles in chunks to avoid blocking the main thread.
    It uses asyncio and ThreadPoolExecutor to run the scraping tasks concurrently.
    """
    existing = []
    chunk_size = 150
    start = 0

    while start < len(titles_links):
        chunk = titles_links[start:start + chunk_size]
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=8) as exec:
            tasks = [
                loop.run_in_executor(exec, get_data, item["title"], item["link"])
                for item in chunk
            ]
            results = await asyncio.gather(*tasks)

        try:
            with open('scraped_news.json', 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except FileNotFoundError:
            existing = []

        existing.extend(results)
        print("extended")

        path_scraped = os.path.join(EXTRA_FILES_FOLDER, 'scraped_news.json')
        with open(path_scraped, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=4)

        start += chunk_size

    return existing

def extract_tickers(ticker_string: str):
    """
    Extract tickers from a string using regex."""
    return re.findall(
        r'([А-Яа-яA-Za-z_()]+(?:\s[А-Яа-яA-Za-z_()]+)*)\s[-+]?\d+(?:,\d+)?%',
        ticker_string
    )

def run(source: str, output_path: str):
    """
    Pipeline to run the entire scraping process.
    It fetches the articles from the given source, scrapes their data,
    processes the data, and saves it to an Excel file.
    """
    if source.startswith(('http://', 'https://')) and '/section/' in source:
        titles_links, short_info = fetch_section(source)
    else:
        if source.startswith(('http://', 'https://')):
            resp = requests.get(source)
            resp.raise_for_status()
            titles_links = resp.json()
        else:
            with open(source, encoding='utf-8') as f:
                titles_links = json.load(f)

        path_unique_short = os.path.join(EXTRA_FILES_FOLDER, 'article_short_info_main.json')
        with open(path_unique_short, encoding='utf-8') as f:
            short_info = json.load(f)

    existing = asyncio.run(scrape_all(titles_links))

    df_news = pd.DataFrame(existing).drop_duplicates(subset=['title'])

    processed = []
    for row in short_info:
        row = row[1:]
        if len(row) == 3:
            row[2] = extract_tickers(row[2])
        else:
            row.append(['IMOEX'])
        processed.append(row)

    df_si = pd.DataFrame(processed, columns=['title', 'short_info', 'shortname'])
    df_expl = df_si.explode('shortname', ignore_index=True)

    all_stocks = Market('shares').tickers()[['ticker', 'shortname']]
    all_stocks.loc[len(all_stocks)] = {'ticker': 'IMOEX', 'shortname': 'IMOEX'}

    df_merge1 = pd.merge(
        df_expl, all_stocks,
        on='shortname', how='left'
    ).dropna(subset=['ticker'])

    df_total = pd.merge(
        df_merge1, df_news,
        on='title', how='left'
    )

    df_total.to_excel(output_path, index=False)
