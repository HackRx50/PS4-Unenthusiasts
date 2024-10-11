import certifi
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os

from pymongo import MongoClient
from settings import Settings
env=Settings();
DB_URL = env.db_url
DB_API_KEY = env.db_api_key
MONGO_URI = env.mongo_uri
MONGO_DB_NAME = env.mongo_db_name

class VectorPineConeDatabaseService:
    def __init__(self, collection_name: str):
        self.client = Pinecone(api_key=DB_API_KEY)
        self.collection_name = collection_name
        self.mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        self.db = self.mongo_client[MONGO_DB_NAME]
        self.collection = self.db[self.collection_name]
        
        
       
        # self.create_collection()
        self.create_knowledgebase_collection()
        
    def create_knowledgebase_collection(self):
        if self.collection.count_documents({"document_name": "knowledgebase"}) == 0:
            self.collection.insert_one({
                "document_name": "knowledgebase",
                "document_names": []  # Array to store document names
            })
            print("Initialized 'knowledgebase' document in 'knowledgebase' collection.")

    def add_document_name(self, document_name: str,document_id: str):
       doc = self.collection.find_one({"document_name": "knowledgebase"})
       if doc:
            document_names = doc.get("documents",[])
            existing_entry = next((entry for entry in document_names if entry["name"] == document_name), None)

            if not existing_entry:
                document_names.append({"name": document_name, "id": document_id})
                self.collection.update_one(
                {"document_name": "knowledgebase"},
                {"$set": {"documents": document_names}}
                )
                print(f"Added document name '{document_name}' with ID '{document_id} to the knowledgebase.")
            else:
                print(f"Document name '{document_name}' already exists in the knowledgebase.")


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
