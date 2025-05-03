from google import genai
from google.genai import types
from podcaster.src import os_helper

class Gemini:
    def __init__(self, system_instructions):
        self.client = genai.Client(api_key=os_helper.getenv('GEMINI_API_KEY'))
        self.system_instructions = system_instructions
        self.model = "gemini-2.0-flash"

    def get_response(self, input):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=input,
                config=types.GenerateContentConfig(
                    system_instruction=[self.system_instructions]
                ),
            )
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None