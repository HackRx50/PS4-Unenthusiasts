from pymongo import MongoClient
import uuid
import os

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
class DatabaseService:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]

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
