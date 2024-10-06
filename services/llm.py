
from openai import OpenAI
from settings import Settings
env=Settings();
LLM_API_KEY=env.openai_api_key
class LLMService:
    def __init__(self ):
        self.client = OpenAI(api_key=LLM_API_KEY)

    def generate_response(self, messages, context_messages=None):
        if context_messages:
            messages += context_messages 

        response = self.client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages,
            
        )
        return response.choices[0].message.content
