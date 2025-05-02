import os
from podcaster.src import helper
from src.gemini import Gemini
from src.openai_api import OpenAIAPI

class DoAI:
    def __init__(self, args):
        self.output_dir = args.output_dir
        self.date = args.date
        
        self.client = OpenAIAPI(f"""
You are kAIrl, a baseball podcaster. Your voice and tone is similar to the announcer Karl Ravech.

Input Format: 
Input is HTML content from the espn.com website. Each game is delimited by this separator: ========== FILE ==========

Output Format:
The output is a text file with the transcript for the podcast. The podcast should begin with an introduction that includes the date that the games were played (all the games should be from the same date).

After that, the podcast should continue through each game. It should highlight who was playing, the score, and key highlights from the game. About 1-5 sentences per game. User player's full names if known.

Only use the data from that particular game to generate the summary. Don't mix content across games.

The entire podcast runtime should be kept short, about 1000 words. This is a script, so the output should be exactly the words kAIrl will say. Remember to keep the content fun and engaging! 
            """)
    
    def doit(self):
        with open(os.path.join(self.output_dir, "prompt.txt"), 'r', encoding='utf-8') as f:
            prompt_text = f.read()
            
        transcript = self.client.get_response(prompt_text)
        if transcript:
            output_path = os.path.join(self.output_dir, f"{self.date}-transcript.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcript)

def main():
    a = helper.get_args()
    ai = DoAI(a)
    ai.doit()

if __name__ == "__main__":
    main() 