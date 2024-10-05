from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

class KnowledgeBaseService:
    def __init__(self, qdrant_url: str, api_key: str, collection_name: str):
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.collection_name = collection_name

    def create_collection(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(collection_name=self.collection_name)

    def search_knowledge_base(self, query_vector, limit: int = 5):
        return self.client.search(collection_name=self.collection_name, query_vector=query_vector, limit=limit)

    def upsert_knowledge_base(self, points: list[PointStruct]):
        self.client.upsert(collection_name=self.collection_name, points=points)
