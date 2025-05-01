from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

class Gemini:
    def __init__(self, system_instructions):
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.system_instructions = system_instructions

    def get_response(self, input):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=input,
                config=types.GenerateContentConfig(
                    system_instruction=[self.system_instructions]
                ),
            )
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None