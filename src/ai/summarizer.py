import os
import google.generativeai as genai
from bs4 import BeautifulSoup
from src.args import get_common_args

class GameSummarizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_summary(self, html_content):
        """Generate a summary of the game using Gemini."""
        try:
            # Extract text from HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)

            # Generate summary
            response = self.model.generate_content(
                f"""Please provide a concise summary of this baseball game. 
                Focus on key moments, notable performances, and the final outcome.
                
                Game details:
                {text}
                """
            )
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    def process_files(self):
        """Process all HTML files in the input directory."""
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.html')]
        if not files:
            print("No HTML files found in input directory.")
            return

        print(f"Processing {len(files)} files...")
        success_count = 0

        for filename in files:
            input_path = os.path.join(self.input_dir, filename)
            output_path = os.path.join(self.output_dir, f"{os.path.splitext(filename)[0]}_summary.txt")

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                summary = self.generate_summary(html_content)
                if summary:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(summary)
                    success_count += 1
                    print(f"Generated summary for: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        print(f"\nSuccessfully generated {success_count} out of {len(files)} summaries.")

def main():
    args = get_common_args('Generate baseball game summaries')

    summarizer = GameSummarizer(args.sanitized_dir, args.output_dir)
    summarizer.process_files()

if __name__ == "__main__":
    main() 