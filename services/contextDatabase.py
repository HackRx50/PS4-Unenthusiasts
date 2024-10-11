from pymongo import MongoClient
import uuid
import os
from settings import Settings
import certifi
env = Settings()

MONGO_URI = env.mongo_uri
MONGO_DB_NAME = env.mongo_db_name
class ContextDatabaseService:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        self.db = self.client[MONGO_DB_NAME]
        self.kbCollection = self.db["knowledgebase"]

    def find_user_by_username(self, username: str):
        return self.db.users.find_one({"username": username})

    def insert_session(self, session_data: dict):
        return self.db.sessions.insert_one(session_data)

    def create_session(self):
        session_id = str(uuid.uuid4())
        self.insert_session({"_id": session_id, "context": []})
        return session_id


    def find_session_by_id(self, session_id: str):
        return self.db.sessions.find_one({"_id": session_id})

    def update_session_context(self, session_id: str, new_context: dict):
        return self.db.sessions.update_one({"_id": session_id}, {"$push": {"context": new_context}})
    
    def create_knowledgebase_collection(self,name):
        

        if self.kbCollection.count_documents({"name": name}) == 0:
            self.kbCollection.insert_one({
                "name": name,
                "document_names": []  # Array to store document names
            })
            print("Initialized 'knowledgebase' document in 'knowledgebase' collection.")

    def add_document_name(self, document_name: str,document_id: str,kb_name:str):
       doc = self.kbCollection.find_one({"document_name": kb_name})
       if doc:
            document_names = doc.get("documents",[])
            existing_entry = next((entry for entry in document_names if entry["name"] == document_name), None)

            if not existing_entry:
                document_names.append({"name": document_name, "id": document_id})
                self.kbCollection.update_one(
                {"document_name": kb_name},
                {"$set": {"documents": document_names}}
                )
                print(f"Added document name '{document_name}' with ID '{document_id} to the knowledgebase.")
            else:
                print(f"Document name '{document_name}' already exists in the knowledgebase.")


