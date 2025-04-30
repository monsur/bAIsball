import os
from bs4 import BeautifulSoup
from src.args import get_common_args, validate_date

class HTMLSanitizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def sanitize_file(self, filename, filter_html=False):
        """Sanitize a single HTML file."""
        input_path = os.path.join(self.input_dir, filename)
        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            if filter_html:
                # Remove script, style, and link tags
                for tag in soup.find_all(['script', 'style', 'link']):
                    tag.decompose()

            # Save sanitized HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            return True
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            return False

    def process_files(self, filter_html=False):
        """Process all HTML files in the input directory."""
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.html')]
        if not files:
            print("No HTML files found in input directory.")
            return

        print(f"Processing {len(files)} files...")
        success_count = 0

        for filename in files:
            if self.sanitize_file(filename, filter_html):
                success_count += 1
                print(f"Processed: {filename}")

        print(f"\nSuccessfully processed {success_count} out of {len(files)} files.")

def main():
    args = get_common_args('Sanitize baseball game HTML files')

    # Validate date format
    if not validate_date(args.date):
        print("Error: Date must be in YYYYMMDD format")
        return

    sanitizer = HTMLSanitizer(args.raw_dir, args.sanitized_dir)
    sanitizer.process_files(filter_html=args.filter)

if __name__ == "__main__":
    main() 