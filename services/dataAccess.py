import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

from settings import Settings
env = Settings()

MONGO_URI = env.mongo_uri

class DataAccess:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client['auth_db']
        self.users_collection = self.db['users']
        self.tier_limits = {'basic': 50, 'premium': 200}

    def get_user_info(self, user_id):
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        return user

    def can_access_data(self, user_id):
        user = self.get_user_info(user_id)
        if not user:
            return {"message": "User not found", "status": False}

        current_time = datetime.datetime.utcnow()
        last_reset = user.get('last_api_reset')

        # If last reset was on a different day, reset the API count
        if not last_reset or last_reset.date() != current_time.date():
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'api_calls_today': 0, 'last_api_reset': current_time}}
            )
            user['api_calls_today'] = 0

        tier = user['tier']
        api_calls_today = user['api_calls_today']
        api_limit = self.tier_limits[tier]

        # Check if the user has remaining API calls
        if api_calls_today < api_limit:
            # Increment the user's API call count
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)}, {'$inc': {'api_calls_today': 1}}
            )
            return {"message": "Data is accessible", "status": True, "user_id": str(user_id)}
        else:
            return {"message": "Maximum API calls reached for the day", "status": False}