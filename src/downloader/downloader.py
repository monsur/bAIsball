import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from src.args import get_common_args

class ContentDownloader:
    def __init__(self, output_dir='output/raw_html'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_box_score_urls(self, scoreboard_url):
        """Extract box score URLs from the MLB scoreboard page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
            response = requests.get(scoreboard_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            box_score_urls = []
            
            # Find all links that contain "box score" in their text
            for link in soup.find_all('a', string=lambda text: text and 'box score' in text.lower()):
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute URLs
                    absolute_url = urljoin(scoreboard_url, href)
                    box_score_urls.append(absolute_url)
            
            return box_score_urls
        except requests.RequestException as e:
            print(f"Error fetching scoreboard page: {e}")
            return []

    def download_content(self, url):
        """Download HTML content from a URL and save it to a file."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Create filename from URL
            filename = f"{url.split('/')[-1]}.html"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return filepath
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def retrieve_scores(self, scoreboard_url, delay=2):
        """Process a scoreboard URL by downloading all box scores."""
        print(f"Fetching box scores from: {scoreboard_url}")
        
        # Get box score URLs
        box_score_urls = self.get_box_score_urls(scoreboard_url)
        
        if not box_score_urls:
            print("No box score URLs found. Exiting.")
            return []
        
        print(f"Found {len(box_score_urls)} box score URLs to process")
        downloaded_files = []
        
        # Download each box score
        for url in box_score_urls:
            print(f"Downloading: {url}")
            filepath = self.download_content(url)
            if filepath:
                print(f"Saved to: {filepath}")
                downloaded_files.append(filepath)
            if url != box_score_urls[-1]:
                time.sleep(delay)
        
        return downloaded_files

def main():
    args = get_common_args('Download baseball game box scores from ESPN')

    downloader = ContentDownloader(args.raw_dir)
    
    # Construct scoreboard URL with date
    scoreboard_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
    downloader.retrieve_scores(scoreboard_url, args.delay)

if __name__ == "__main__":
    main() 