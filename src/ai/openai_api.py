from openai import OpenAI
from dotenv import load_dotenv
import os

class OpenAIAPI:
   def __init__(self, system_instructions):
      load_dotenv()
      self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
      self.system_instructions = system_instructions
      
   def get_response(self, input):
      try:
         response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
               {
                     "role": "developer",
                     "content": self.system_instructions
               },
               {
                     "role": "user",
                     "content": input
               }
            ])
         return response.output_text
      except Exception as e:
         print(f"Error generating summary: {e}")
         return None
