from openai import OpenAI
from dotenv import load_dotenv
import os
from src.args import get_common_args

class PodcastAudio:
   def __init__(self):
      load_dotenv()
      self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
      
   def create(self, content, output_dir, date):
    try:
        speech_file_path = os.path.join(output_dir, f"{date}_summary.mp3")


        with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="ash",
            input=content,
            instructions="Speak like a sportscaster, similar to Karl Ravech",
        ) as response:
            response.stream_to_file(speech_file_path)
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def main():
    args = get_common_args('Generate baseball game summaries')
    
    input_path = os.path.join(args.output_dir, f"{args.date}_summary.txt")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        podcast = PodcastAudio()
        podcast.create(content, args.output_dir, args.date)

if __name__ == "__main__":
    main() 