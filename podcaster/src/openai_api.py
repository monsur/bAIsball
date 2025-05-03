from openai import OpenAI
from podcaster.src import os_helper

class OpenAIAPI:
   def __init__(self, system_instructions):
      self.client = OpenAI(api_key=os_helper.getenv('OPENAI_API_KEY'))
      self.system_instructions = system_instructions
      self.model = "gpt-4.1-mini"
      self.temperature = 0.2
      
   def get_response(self, input):
      try:
         response = self.client.responses.create(
            model=self.model,
            input=[
               {
                     "role": "developer",
                     "content": self.system_instructions
               },
               {
                     "role": "user",
                     "content": input
               }
            ], temperature=self.temperature)
         return response.output_text
      except Exception as e:
         print(f"Error generating summary: {e}")
         return None
