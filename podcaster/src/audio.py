import os
from dotenv import load_dotenv
from openai import OpenAI
from podcaster.src import helper

logger = helper.get_logger()

class PodcastAudio:
   def __init__(self, args):
      load_dotenv()
      self.args = args
      self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
      
   def create(self):
    input_path = os.path.join(self.args.output_dir, f"{self.args.date}-transcript.txt")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        speech_file_path = os.path.join(self.args.output_dir, f"{self.args.date}-audio.mp3")

        with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="ash",
            input=content,
            instructions="""
            Voice Affect: Energetic and animated; dynamic with variations in pitch and tone.

Tone: Excited and enthusiastic, conveying an upbeat and thrilling atmosphere. 

Pacing: Rapid delivery when describing the game or the key moments (e.g., "an overtime thriller," "pull off an unbelievable win") to convey the intensity and build excitement.

Slightly slower during dramatic pauses to let key points sink in.

Emotion: Intensely focused, and excited. Giving off positive energy.

Personality: Relatable and engaging. 

Pauses: Short, purposeful pauses after key moments in the game.
            """,
        ) as response:
            response.stream_to_file(speech_file_path)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return None

def main():
    a = helper.get_args()
    p = PodcastAudio(a)
    p.create()

if __name__ == "__main__":
    main() 