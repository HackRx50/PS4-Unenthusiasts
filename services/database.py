from pymongo import MongoClient

class DatabaseService:
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def find_user_by_username(self, username: str):
        return self.db.users.find_one({"username": username})

    def insert_session(self, session_data: dict):
        return self.db.sessions.insert_one(session_data)

    def find_session_by_id(self, session_id: str):
        return self.db.sessions.find_one({"_id": session_id})

    def update_session_context(self, session_id: str, new_context: dict):
        return self.db.sessions.update_one({"_id": session_id}, {"$push": {"context": new_context}})
