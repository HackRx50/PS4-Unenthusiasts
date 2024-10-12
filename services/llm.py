
from openai import OpenAI
import time
from settings import Settings
env=Settings();
LLM_API_KEY=env.openai_api_key
class LLMService:
    def __init__(self ):
        self.client = OpenAI(api_key=LLM_API_KEY)

    def generate_response(self, messages, context_messages=None):
        startT=time.time()
        if context_messages:
            messages += context_messages 

        response = self.client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            
        )
        endT=time.time()
        dur=endT-startT
        print(f"Time taken to fetch from GPT: {dur:.4f} seconds")


        return response.choices[0].message.content
