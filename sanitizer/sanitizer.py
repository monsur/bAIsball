import os
from bs4 import BeautifulSoup
import argparse

class ContentSanitizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

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

    def process_files(self, enable_filter=True):
        """Process all HTML files in the input directory."""
        for filename in os.listdir(self.input_dir):
            if not filename.endswith('.html'):
                continue
                
            input_path = os.path.join(self.input_dir, filename)
            output_path = os.path.join(self.output_dir, filename)
            
            print(f"Processing: {filename}")
            
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if enable_filter:
                    filtered_content = self.filter_html(content)
                    if filtered_content:
                        content = filtered_content
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Saved to: {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Sanitize baseball game HTML content')
    parser.add_argument('--input-dir', type=str, default='raw_html',
                       help='Directory containing input HTML files (default: raw_html)')
    parser.add_argument('--output-dir', type=str, default='sanitized_html',
                       help='Directory to save sanitized files (default: sanitized_html)')
    parser.add_argument('--no-filter', action='store_true',
                       help='Disable HTML filtering (files will be copied as-is)')
    args = parser.parse_args()

    sanitizer = ContentSanitizer(args.input_dir, args.output_dir)
    sanitizer.process_files(not args.no_filter)

if __name__ == "__main__":
    main() 