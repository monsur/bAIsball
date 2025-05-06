from openai import OpenAI
from podcaster.src import args_helper
from podcaster.src import logger_helper
from podcaster.src import os_helper

logger = logger_helper.get_logger(__name__)

def run(args):
    client = OpenAI(api_key=os_helper.getenv('OPENAI_API_KEY'))

    content = os_helper.read_file(args.output_dir, f"{args.date}-transcript.txt")

    try:
        speech_file_path = os_helper.join(args.output_dir, f"{args.date}-audio.mp3")

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="ash",
            input=content,
            instructions="""
Voice Affect: Energetic and animated; dynamic with variations in pitch and tone.

Tone: Excited and enthusiastic, conveying an upbeat and thrilling atmosphere. 

Pacing: Rapid delivery when describing the game or the key moments (e.g., "an overtime thriller," "pull off an unbelievable win") to convey the intensity and build excitement. Slightly slower during dramatic pauses to let key points sink in.

Emotion: Intensely focused, and excited. Giving off positive energy.

Personality: Relatable and engaging. 

Pauses: Short, purposeful pauses after key moments in the game.
            """,
        ) as response:
            response.stream_to_file(speech_file_path)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return None

if __name__ == "__main__":
    run(args_helper.get_args())
