from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import os
from settings import Settings
env=Settings();
DB_URL = env.db_url
DB_API_KEY = env.db_api_key
class VectorContextDatabaseService:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(url=DB_URL, api_key=DB_API_KEY,timeout=60)
        self.collection_name = collection_name
        self.create_collection()

    def create_collection(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(collection_name=self.collection_name)

    def search(self, query_embedding, limit=5, filter=None):
        return self.client.scroll(
            collection_name=self.collection_name,  # Use 'vector' to specify the query embedding
            limit=limit,
            scroll_filter=filter,
            with_vectors=True  # If you want to return vectors in the result
        )


    def upsert(self, points):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

   