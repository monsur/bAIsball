import os
from bs4 import BeautifulSoup, Comment
from src.args import get_common_args

class ContentSanitizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

    def sanitize_file(self, filename, filter_html=False, prettyprint=False):
        """Sanitize a single HTML file."""
        input_path = os.path.join(self.input_dir, filename)
        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            if filter_html:
                # Remove script, style, link, and img tags
                for tag in soup.find_all(['script', 'style', 'link', 'img']):
                    tag.decompose()

                # Remove HTML comments
                for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                    comment.extract()

                # Remove HeaderScoreboardWrapper div
                for div in soup.find_all('div', class_='HeaderScoreboardWrapper'):
                    div.decompose()

                # Remove PageLayout page-container cf page-footer-container div
                for div in soup.find_all('div', class_='PageLayout page-container cf page-footer-container'):
                    div.decompose()

                # Remove fittOverlayContainer div
                for div in soup.find_all('div', id='fittOverlayContainer'):
                    div.decompose()

                # Remove fittBGContainer div
                for div in soup.find_all('div', id='fittBGContainer'):
                    div.decompose()

                # Remove lightboxContainer div
                for div in soup.find_all('div', id='lightboxContainer'):
                    div.decompose()

                # Remove Site Header Wrapper div
                for div in soup.find_all('header', class_='db Site__Header__Wrapper sticky'):
                    div.decompose()

                # Remove all classes from all tags
                for tag in soup.find_all(True):  # True matches all tags
                    if 'class' in tag.attrs:
                        del tag.attrs['class']

            # Get the HTML content
            if prettyprint:
                html_content = soup.prettify()
            else:
                html_content = str(soup)
                # Remove empty lines
                lines = [line for line in html_content.split('\n') if line.strip()]
                html_content = '\n'.join(lines)

            # Save sanitized HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            return False

    def process_files(self, filter_html=False, prettyprint=False):
        """Process all HTML files in the input directory."""
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.html')]
        if not files:
            print("No HTML files found in input directory.")
            return

        print(f"Processing {len(files)} files...")
        success_count = 0

        for filename in files:
            if self.sanitize_file(filename, filter_html, prettyprint):
                success_count += 1
                print(f"Processed: {filename}")

        print(f"\nSuccessfully processed {success_count} out of {len(files)} files.")

def main():
    args = get_common_args('Sanitize baseball game HTML files')

    sanitizer = ContentSanitizer(args.raw_dir, args.sanitized_dir)
    sanitizer.process_files(filter_html=args.filter, prettyprint=args.prettyprint)

if __name__ == "__main__":
    main() 