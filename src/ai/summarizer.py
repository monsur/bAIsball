import os
import google.generativeai as genai
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

class GameSummarizer:
    def __init__(self, input_dir, output_dir):
        # Initialize Gemini API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_system_instructions(self):
        """Read system instructions from file."""
        try:
            instructions_path = os.path.join(os.path.dirname(__file__), 'system_instructions.txt')
            with open(instructions_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading system instructions: {e}")
            return None

    def generate_summary(self, html_contents):
        """Generate a summary using Gemini AI."""
        try:
            # Get system instructions from file
            system_instructions = self.get_system_instructions()
            if not system_instructions:
                return None
            
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
            filename = "podcast_transcript.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
        except Exception as e:
            print(f"Error saving summary: {e}")
            return None

    def process_files(self):
        """Process all HTML files in the input directory."""
        html_contents = []
        
        for filename in os.listdir(self.input_dir):
            if not filename.endswith('.html'):
                continue
                
            filepath = os.path.join(self.input_dir, filename)
            print(f"Reading: {filename}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                html_contents.append(content)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        
        if not html_contents:
            print("No valid HTML content found. Exiting.")
            return
        
        print("Generating summary...")
        summary = self.generate_summary(html_contents)
        
        if summary:
            filepath = self.save_summary(summary)
            print(f"Summary saved to: {filepath}")

def main():
    parser = argparse.ArgumentParser(description='Generate baseball game summaries using AI')
    parser.add_argument('--input-dir', type=str, default='output/sanitized_html',
                       help='Directory containing input HTML files (default: output/sanitized_html)')
    parser.add_argument('--output-dir', type=str, default='output/summaries',
                       help='Directory to save summary files (default: output/summaries)')
    args = parser.parse_args()

    summarizer = GameSummarizer(args.input_dir, args.output_dir)
    summarizer.process_files()

if __name__ == "__main__":
    main() 