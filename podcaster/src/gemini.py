from google import genai
from google.genai import types
from podcaster.src import os_helper

class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=os_helper.getenv('GEMINI_API_KEY'))
        self.model = "gemini-2.5-pro-exp-03-25"

    def get_response(self, input, system_instructions):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=input,
                config=types.GenerateContentConfig(
                    system_instruction=[system_instructions],
                    temperature=0.2
                ),
            )
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None