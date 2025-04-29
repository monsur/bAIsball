import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class GameHTMLProcessor:
    def __init__(self):
        # Create directories if they don't exist
        self.html_dir = 'html_files'
        os.makedirs(self.html_dir, exist_ok=True)

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

    def generate_summary(self, html_content, output_format='text'):
        """Generate a summary using Gemini AI with specified output format."""
        try:
            # System instructions for Gemini
            system_instructions = """You are creating a summary of baseball games for a newsletter. 

            The input is provided as HTML from the espn.com website. 

            For each input file, follow these steps:
            1. Parse the HTML and extract relevant details about the baseball game.
            2. Don't include the filename in the output.
            3. First line of output: Concisely show the teams that played and the score of the game in the format: away team (away team score) vs home team (home team score)
            4. Second line of output: Show a concise date and time and timezone of the game (no heading needed, just the date/time)
            5. Rest of output: Any highlights or strong performances from the game. There should be 1-5 highlights per-game, provided in bullet format. When appropriate ,include the names of players who were part of the highlight. Order the bullets in inning order, with the earlier innings first.

            If there's a file named "standings.txt", these are the league standings for each time. Use this data to provide context for each game in the summary, but only if it's appropriate. Also if there's a standings.txt file, show each team's record at the beginning, after the date."""
            
            # Add format-specific instructions
            if output_format == 'html':
                system_instructions += "\n\nFormat the output as HTML with appropriate tags. Use <h2> for the game title, <p> for paragraphs, and <ul>/<li> for bullet points. Do not include <html>, <head>, or <body> tags."
            elif output_format == 'text':
                system_instructions += "\n\nFormat the output as plain text with clear line breaks and bullet points using '-' characters."
            
            prompt = f"""Please provide a concise summary of this baseball game content. 
            Focus on key plays, scores, and important moments. 
            Content: {html_content}"""
            
            # Create a chat session with system instructions
            chat = self.model.start_chat(history=[])
            response = chat.send_message(system_instructions + "\n\n" + prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    def save_combined_summaries(self, summaries, output_format='text'):
        """Save all summaries to a single file with specified format."""
        try:
            # Determine file extension and wrapper based on format
            if output_format == 'html':
                extension = '.html'
                wrapper_start = """<!DOCTYPE html>
<html>
<head>
    <title>Baseball Game Summaries</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .game { margin-bottom: 40px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }
        h2 { color: #333; }
        ul { margin-left: 20px; }
    </style>
</head>
<body>
"""
                wrapper_end = "</body>\n</html>"
                separator = "\n<div class='game'>\n"
            else:
                extension = '.txt'
                wrapper_start = "BASEBALL GAME SUMMARIES\n" + "=" * 50 + "\n\n"
                wrapper_end = ""
                separator = "\n" + "-" * 50 + "\n\n"
            
            # Create the combined content
            combined_content = wrapper_start + separator.join(summaries) + wrapper_end
            
            # Save to file
            filename = f"all_summaries{extension}"
            filepath = os.path.join(self.summaries_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            return filepath
        except Exception as e:
            print(f"Error saving combined summaries: {e}")
            return None

def main():
    # Example usage
    html_processor = GameHTMLProcessor()
    summarizer = GameSummarizer()
    
    # Example URLs (replace with actual baseball game URLs)
    urls = [
        "https://www.espn.com/mlb/recap/_/gameId/401695316",
        "https://www.espn.com/mlb/boxscore/_/gameId/401695317"
    ]
    
    # Lists to store summaries
    html_summaries = []
    text_summaries = []
    
    # Flag to control HTML filtering
    filter_html = False  # Set to True to enable filtering
    
    for url in urls:
        # Download HTML
        html_content = html_processor.download_html(url)
        if not html_content:
            continue
        
        # Optionally filter HTML
        if filter_html:
            html_content = html_processor.filter_html(html_content)
            if not html_content:
                continue
        
        # Generate HTML summary
        html_summary = summarizer.generate_summary(html_content, output_format='html')
        if html_summary:
            html_summaries.append(html_summary)
        
        # Generate text summary
        text_summary = summarizer.generate_summary(html_content, output_format='text')
        if text_summary:
            text_summaries.append(text_summary)
        
        time.sleep(2)  # Add delay between requests
    
    # Save combined summaries
    if html_summaries:
        html_path = summarizer.save_combined_summaries(html_summaries, output_format='html')
        print(f"Combined HTML summaries saved to: {html_path}")
    
    if text_summaries:
        text_path = summarizer.save_combined_summaries(text_summaries, output_format='text')
        print(f"Combined text summaries saved to: {text_path}")

if __name__ == "__main__":
    main() 