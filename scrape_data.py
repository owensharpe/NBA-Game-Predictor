# SCRAPING NBA DATA

# import libraries
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time


# global variables
seasons = list(range(2016, 2024))
DATA_DIR = "data"
STANDINGS_DIR = os.path.join(DATA_DIR, "standings")
SCORES_DIR = os.path.join(DATA_DIR, "scores")


# created function that gets the html
def get_html(url, selector, sleep=5, retries=3):

    # initialize the html
    html_file = None

    # essentially attempt to web scrape with multiple tries
    for i in range(1, retries + 1):
        time.sleep(sleep * i)

        # using playwright to attempt to scrape, but if error is thrown, keep going
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                print(page.title())
                html_file = page.inner_html(selector)
        except PlaywrightTimeout:
            print(f"Timeout error on {url}")
            continue
        else:
            break
    return html_file


# created function that scrapes individual season
def scrape_season(season):

    nba_url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"

    # call the get_html function to get the html
    html = get_html(nba_url, "#content .filter")

    # using BeautifulSoup library
    soup = BeautifulSoup(html)

    # find all the a-tags
    links = soup.find_all('a')
    href = [link['href'] for link in links]
    standings_pages = [f"https://basketball-reference.com{link}" for link in href]

    # save file path to the directory
    for url in standings_pages:
        save_path = os.path.join(STANDINGS_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue

        # save the html
        html = get_html(url, "#all_schedule")
        with open(save_path, "w+") as f:
            f.write(html)


# created function that scrapes individual game
def scrape_game(standing_file):

    with open(standing_file, "r") as f:
        html = f.read()

    # parse with BeautifulSoup
    soup = BeautifulSoup(html)

    # get a-tags for box scores
    links = soup.find_all('a')
    hrefs = [link.get('href') for link in links]
    box_scores = [link for link in hrefs if link and 'boxscore' in link and ".html" in link]
    box_scores = [f"https://www.basketball-reference.com{link}" for link in box_scores]

    # obtaining box scores
    for url in box_scores:
        save_path = os.path.join(SCORES_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue

        html = get_html(url, "#content")
        if not html:
            continue
        with open(save_path, "w+") as f:
            f.write(html)


# scraping the data
if __name__ == "__main__":

    # loop through each season and scrape
    for current_season in seasons:
        scrape_season(current_season)

    # get standing files and filter
    standing_files = os.listdir(STANDINGS_DIR)
    standing_files = [s for s in standing_files if ".html" in s]

    # scrape game files
    for f in standing_files:
        filepath = os.path.join(STANDINGS_DIR, f)
        scrape_game(filepath)

