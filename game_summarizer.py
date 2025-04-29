import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import time
from urllib.parse import urljoin
import argparse
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class GameHTMLProcessor:
    def __init__(self):
        # Create directories if they don't exist
        self.html_dir = 'html_files'
        os.makedirs(self.html_dir, exist_ok=True)

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

    def download_html(self, url):
        """Download HTML content from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def filter_html(self, html_content):
        """Filter HTML to keep only specified nodes."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            new_soup = BeautifulSoup('', 'html.parser')
            
            # Keep title node
            title = soup.find('title')
            if title:
                new_soup.append(title)
            
            # Keep Gamestrip nodes
            gamestrip_nodes = soup.find_all(lambda tag: 
                (tag.get('id') and 'Gamestrip' in tag['id']) or
                (tag.get('class') and any('Gamestrip' in c for c in tag['class']))
            )
            for node in gamestrip_nodes:
                new_soup.append(node)
            
            # Keep Athletes_Container nodes
            athletes_nodes = soup.find_all(lambda tag: 
                (tag.get('id') and 'Athletes_Container' in tag['id']) or
                (tag.get('class') and 'Athletes_Container' in tag['class'])
            )
            for node in athletes_nodes:
                new_soup.append(node)
            
            # Keep GameInfo nodes
            gameinfo_nodes = soup.find_all(lambda tag: 
                (tag.get('id') and 'GameInfo' in tag['id']) or
                (tag.get('class') and 'GameInfo' in tag['class'])
            )
            for node in gameinfo_nodes:
                new_soup.append(node)
            
            # Keep ScoringSummary nodes
            scoring_nodes = soup.find_all(lambda tag: 
                (tag.get('id') and 'ScoringSummary' in tag['id']) or
                (tag.get('class') and any('ScoringSummary' in c for c in tag['class']))
            )
            for node in scoring_nodes:
                new_soup.append(node)
            
            # Keep table in Card section
            card_sections = soup.find_all('section', class_='Card')
            for section in card_sections:
                table = section.find('table')
                if table:
                    new_soup.append(table)
            
            return str(new_soup)
        except Exception as e:
            print(f"Error filtering HTML: {e}")
            return None

class GameSummarizer:
    def __init__(self):
        # Initialize Gemini API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-pro-exp-03-25')
        
        # Create directories if they don't exist
        self.summaries_dir = 'summaries'
        os.makedirs(self.summaries_dir, exist_ok=True)

    def generate_summary(self, html_contents):
        """Generate a summary using Gemini AI."""
        try:
            # System instructions for Gemini
            system_instructions = """You are kAIrl, a baseball podcaster. Your voice and tone is similar to the announcer Karl Ravech.

Input Format: 
Input is one or more HTML files from the espn.com website. Each HTML file represents the results of one game. There may also be an optional file named "standings.html" that includes the stands of each team in the league.

Output Format:
The output is a text file with the transcript for the podcast. The podcast should begin with an introduction that includes the date that the games were played (all the games should be from the same date). Next the podcast should highlight 2-3 of the most key moments from all the days games.

After that, the podcast should continue through each game. It should highlight who was playing, the score, and key highlights from the game.

The entire podcast runtime should be kept short, about 15-20minutes. Remember to keep the content fun and engaging!"""
            
            # Create a chat session with system instructions
            chat = self.model.start_chat(history=[])
            
            # Prepare the prompt with all HTML contents
            prompt = "Here are the game summaries for today's baseball games:\n\n"
            for i, content in enumerate(html_contents, 1):
                prompt += f"Game {i}:\n{content}\n\n"
            
            # Send a single request with all content
            response = chat.send_message(system_instructions + "\n\n" + prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    def save_summary(self, summary):
        """Save the summary to a text file."""
        try:
            # Add header to the content
            content = "BASEBALL GAME SUMMARIES\n" + "=" * 50 + "\n\n" + summary
            
            # Save to file
            filename = "all_summaries.txt"
            filepath = os.path.join(self.summaries_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
        except Exception as e:
            print(f"Error saving summary: {e}")
            return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate baseball game summaries from ESPN box scores')
    parser.add_argument('--date', type=str, help='Date in YYYYMMDD format (default: yesterday)', 
                       default=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
    parser.add_argument('--filter', action='store_true', help='Enable HTML filtering')
    parser.add_argument('--delay', type=int, default=60, 
                       help='Delay in seconds between API calls (default: 60)')
    args = parser.parse_args()

    # Validate date format
    try:
        datetime.strptime(args.date, '%Y%m%d')
    except ValueError:
        print("Error: Date must be in YYYYMMDD format")
        return

    # Example usage
    html_processor = GameHTMLProcessor()
    summarizer = GameSummarizer()
    
    # Configuration
    api_delay_seconds = args.delay
    filter_html = args.filter
    
    # Construct scoreboard URL with date
    scoreboard_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
    print(f"Fetching box scores for date: {args.date}")
    print(f"Scoreboard URL: {scoreboard_url}")
    
    # Get box score URLs from the scoreboard
    box_score_urls = html_processor.get_box_score_urls(scoreboard_url)
    
    if not box_score_urls:
        print("No box score URLs found. Exiting.")
        return
    
    print(f"Found {len(box_score_urls)} box score URLs to process")
    
    # Collect all HTML contents
    html_contents = []
    
    for url in box_score_urls:
        print(f"Processing: {url}")
        
        # Download HTML
        html_content = html_processor.download_html(url)
        if not html_content:
            continue
        
        # Optionally filter HTML
        if filter_html:
            html_content = html_processor.filter_html(html_content)
            if not html_content:
                continue
        
        html_contents.append(html_content)
        
        # Wait before processing next URL
        if url != box_score_urls[-1]:  # Don't wait after the last URL
            print(f"Waiting {api_delay_seconds} seconds before next request...")
            time.sleep(api_delay_seconds)
    
    if not html_contents:
        print("No valid HTML content found. Exiting.")
        return
    
    # Generate summary in one API call
    print("Generating summary...")
    summary = summarizer.generate_summary(html_contents)
    
    # Save summary
    if summary:
        filepath = summarizer.save_summary(summary)
        print(f"Summary saved to: {filepath}")

if __name__ == "__main__":
    main() 