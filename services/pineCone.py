from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from settings import Settings
env=Settings();
DB_URL = env.db_url
DB_API_KEY = env.db_api_key

class VectorPineConeDatabaseService:
    def __init__(self, collection_name: str):
        self.client = Pinecone(api_key="f91cfbc7-6ea4-4ed4-a444-aaea7d7ff569")
        self.collection_name = collection_name
        self.create_collection()

    def create_collection(self):
        existing_indexes = self.client.list_indexes()
        if not self.collection_name not in existing_indexes:
            self.client.create_index(
                name=self.collection_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws', 
                    region='us-east-1'
                ) 
            )

    def search(self, query_embedding, limit=5, document_id=None):
        index = self.client.Index(self.collection_name)
        return index.query(
            vector=query_embedding,  # Pass the query vector (embedding)
            top_k=limit,  # Set the number of results to retrieve
            namespace=self.collection_name,  # Use namespace to filter within a logical partition (equivalent to collection in Qdrant)
            filter={
                "document_id":{"$eq":document_id}
                },# Apply metadata filtering if needed (optional)
            includeMetadata=True,
            # include_values=True
        )



    def upsert(self, points):
        index = self.client.Index(self.collection_name)
        index.upsert(
            namespace=self.collection_name,
            vectors=points
        )
