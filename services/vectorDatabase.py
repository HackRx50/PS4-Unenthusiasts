from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import os

DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")

class VectorContextDatabaseService:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(url=DB_URL, api_key=DB_API_KEY)
        self.collection_name = collection_name
        self.create_collection()

    def create_collection(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(collection_name=self.collection_name)

    def search(self, query_embedding, limit=5):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )

    def upsert(self, points):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
