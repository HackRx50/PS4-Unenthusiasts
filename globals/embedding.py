from langchain_community.embeddings.openai import OpenAIEmbeddings
import os
from settings import Settings

env=Settings()
OPENAI_API_KEY = env.openai_api_key
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings