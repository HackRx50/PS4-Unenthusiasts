from langchain_community.embeddings.openai import OpenAIEmbeddings
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings