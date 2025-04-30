import os
from bs4 import BeautifulSoup
import argparse

class ContentSanitizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def filter_html(self, html_content):
        """Remove script, style, and link tags from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove all script tags
            for script in soup.find_all('script'):
                script.decompose()
            
            # Remove all style tags
            for style in soup.find_all('style'):
                style.decompose()
            
            # Remove all link tags
            for link in soup.find_all('link'):
                link.decompose()
            
            return str(soup)
        except Exception as e:
            print(f"Error filtering HTML: {e}")
            return None

    def process_files(self, enable_filter=False):
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
    parser = argparse.ArgumentParser(description='Process baseball game HTML content')
    parser.add_argument('--input-dir', type=str, default='output/raw_html',
                       help='Directory containing input HTML files (default: output/raw_html)')
    parser.add_argument('--output-dir', type=str, default='output/sanitized_html',
                       help='Directory to save processed files (default: output/sanitized_html)')
    parser.add_argument('--filter', action='store_true',
                       help='Remove script, style, and link tags from HTML files')
    args = parser.parse_args()

    sanitizer = ContentSanitizer(args.input_dir, args.output_dir)
    sanitizer.process_files(args.filter)

if __name__ == "__main__":
    main() 