import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.args import get_common_args

load_dotenv()

class GameSummarizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Gemini
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    def generate_summary(self, content):
        """Generate a summary of the game using Gemini."""
        try:

            # Generate summary
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=content,
                config=types.GenerateContentConfig(
        system_instruction=[
            f"""
You are kAIrl, a baseball podcaster. Your voice and tone is similar to the announcer Karl Ravech.

Input Format: 
Input is one or more HTML files from the espn.com website. Each HTML file represents the results of one game. There may also be an optional file named "standings.html" that includes the stands of each team in the league.

Output Format:
The output is a text file with the transcript for the podcast. The podcast should begin with an introduction that includes the date that the games were played (all the games should be from the same date). Next the podcast should highlight 2-3 of the most key moments from all the days games.

After that, the podcast should continue through each game. It should highlight who was playing, the score, and key highlights from the game.

The entire podcast runtime should be kept short, about 15-20minutes. Remember to keep the content fun and engaging! 
            """
        ]
    ),
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

        content = ""
        for filename in files:
            input_path = os.path.join(self.input_dir, filename)

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    content += "\n\n" + html_content
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        summary = self.generate_summary(content)
        print(summary)

def main():
    args = get_common_args('Generate baseball game summaries')

    summarizer = GameSummarizer(args.sanitized_dir, args.output_dir)
    summarizer.process_files()

if __name__ == "__main__":
    main() 