import logging
import os
import requests
import time
from bs4 import BeautifulSoup
from podcaster.src import helper
from urllib.parse import urljoin

logger = helper.get_logger()

class DataDownloader:
    def __init__(self, args):
        self.source_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
        self.output_dir = os.path.join(args.output_dir, "data")
        self.delay = args.delay
        helper.make_dir(self.output_dir, True)

    def make_request(self, url):
        logger.info(f"Retrieving {url}")
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            })
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def get_boxscore_urls(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        boxscore_urls = []

        # Find all links that contain "box score" in their text
        for link in soup.find_all('a', string=lambda text: text and 'box score' in text.lower()):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(self.source_url, href)
                boxscore_urls.append(absolute_url)
            
        return boxscore_urls

    def save_boxscore_data(self, url):
        boxscore_html = self.make_request(url)
            
        # Create filename from URL
        filename = f"{url.split('/')[-1]}-boxscore.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save HTML content
        with open(filepath, 'w', encoding='utf-8') as f:
            logger.info(f"Writing file {filepath}")
            f.write(boxscore_html)

    def save_recap_data(self, url):
        url = url.replace("boxscore", "recap")
        recap_html = self.make_request(url)
            
        # Create filename from URL
        filename = f"{url.split('/')[-1]}-recap.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save HTML content
        with open(filepath, 'w', encoding='utf-8') as f:
            logger.info(f"Writing file {filepath}")
            f.write(recap_html)

    def retrieve_data(self):
        logger.info(f"Fetching box scores from: {self.source_url}")
        
        source_html = self.make_request(self.source_url)
        
        boxscore_urls = self.get_boxscore_urls(source_html)
        logger.info(f"Found {len(boxscore_urls)} games")
        
        for boxscore_url in boxscore_urls:
            self.save_boxscore_data(boxscore_url)
            self.save_recap_data(boxscore_url)
            time.sleep(self.delay)
        
def main():
    a = helper.get_args()
    downloader = DataDownloader(a)
    downloader.retrieve_data()

if __name__ == "__main__":
    main() 