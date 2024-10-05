
from openai import OpenAI

class LLMService:
    def __init__(self, api_key: str):
        self.client = OpenAI()
        self.api_key = api_key

    def generate_response(self, messages, context_messages=None):
        if context_messages:
            messages += context_messages 

        response = self.client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages
        )
        return response.choices[0].message.content
