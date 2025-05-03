import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from podcaster.src import args_helper
from podcaster.src import logger_helper
from podcaster.src import os_helper

logger = logger_helper.get_logger(__name__)

def run(args):

    def get_boxscore_urls(html, source_url):
        soup = BeautifulSoup(html, 'html.parser')
        boxscore_urls = []

        # Find all links that contain "box score" in their text
        for link in soup.find_all('a', string=lambda text: text and 'box score' in text.lower()):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(source_url, href)
                boxscore_urls.append(absolute_url)
            
        return boxscore_urls
    
    def save_data(url, suffix):
        html = make_request(url)
            
        # Create filename from URL
        filename = f"{url.split('/')[-1]}-{suffix}.html"
        filepath = os_helper.join(args.output_data_dir, filename)
        
        # Save HTML content
        with open(filepath, 'w', encoding='utf-8') as f:
            logger.info(f"Writing file {filepath}")
            f.write(html)

    def make_request(url):
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

    source_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
    logger.info(f"Fetching box scores from: {source_url}")

    source_html = make_request(source_url)
        
    boxscore_urls = get_boxscore_urls(source_html, source_url)
    logger.info(f"Found {len(boxscore_urls)} games")
        
    for boxscore_url in boxscore_urls:
        save_data(boxscore_url, "boxscore")
        time.sleep(args.delay)
        save_data(boxscore_url.replace("boxscore", "recap"), "recap")
        time.sleep(args.delay)
        
def main():
    a = args_helper.get_args()
    run(a)

if __name__ == "__main__":
    main() 