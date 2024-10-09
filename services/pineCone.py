from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from settings import Settings
env=Settings();
DB_URL = env.db_url
DB_API_KEY = env.db_api_key

class VectorPineConeDatabaseService:
    def __init__(self, collection_name: str):
        self.client = Pinecone(api_key=DB_API_KEY)
        self.collection_name = collection_name
       
        # self.create_collection()

    def create_collection(self):
        existing_indexes = self.client.list_indexes()
        if  self.collection_name not in existing_indexes:
            self.client.create_index(
                name=self.collection_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws', 
                    region='us-east-1'
                ) 
            )
        

    def searchWithFilter(self, query_embedding, document_id,limit=5):
        index = self.client.Index(self.collection_name)
        return index.query(
            namespace="knowledgebase",
            vector=query_embedding,  # Pass the query vector (embedding)
            top_k=limit,  # Set the number of results to retrieve  
            filter={"document_id":{"$eq":document_id}},
            include_metadata=True
            # include_values=True
        )

    def search(self, query_embedding, limit=5):
        index = self.client.Index(self.collection_name)
        return index.query(
            namespace="knowledgebase",
            vector=query_embedding,  # Pass the query vector (embedding)
            top_k=limit,  # Set the number of results to retrieve  
            include_metadata=True
            # include_values=True
        )
        



    def upsert(self, points):
        index = self.client.Index(self.collection_name)
        index.upsert(
            namespace=self.collection_name,
            vectors=points,
            batch_size=50
        )
