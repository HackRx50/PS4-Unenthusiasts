import datetime
import os
import jwt
import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
from settings import Settings
env=Settings();


JWT_SECRET = env.jwt_secret_key
JWT_REFRESH_SECRET = env.jwt_refresh_secret
MONGO_URI = env.mongo_uri


class Auth:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        self.db = self.client['auth_db']
        self.users_collection = self.db['users']

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def check_password(self, hashed_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def generate_jwt_token(self, user_id):
        payload = {
            'user_id': str(user_id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=25),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return token

    def generate_refresh_token(self, user_id):
        payload = {
            'user_id': str(user_id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
        }
        refresh_token = jwt.encode(
            payload, JWT_REFRESH_SECRET, algorithm='HS256')
        return refresh_token

    def register_user(self, username, email, password):
        if self.users_collection.find_one({'email': email}):
            return {"message": "User already exists", "status": False}

        hashed_password = self.hash_password(password)
        new_user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'tier': 'basic',  # Add 'tier' field with default value 'basic'
            'api_calls_today': 0,
            'last_api_reset': datetime.datetime.utcnow()
        }
        result = self.users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        access_token = self.generate_jwt_token(user_id)
        refresh_token = self.generate_refresh_token(user_id)
        return {"message": "User registered successfully", "status": True, "user_id": user_id, "access_token": access_token, "refresh_token": refresh_token, "email": email , "username": username}

    def login_user(self, email, password):
        user = self.users_collection.find_one({'email': email})
        if not user:
            return {"message": "Invalid email or password", "status": False}

        if not self.check_password(user['password'], password):
            return {"message": "Invalid email or password", "status": False}

        user_id = user['_id']
        access_token = self.generate_jwt_token(user_id)
        refresh_token = self.generate_refresh_token(user_id)

        return {"message": "Login successful", "status": True, "access_token": access_token, "refresh_token": refresh_token, "email": user['email'] , "username": user['username']}

    def refresh_access_token(self, refresh_token):
        try:
            decoded_token = jwt.decode(
                refresh_token, JWT_REFRESH_SECRET, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            new_access_token = self.generate_jwt_token(user_id)
            return {"access_token": new_access_token, "status": True}
        except jwt.ExpiredSignatureError:
            return {"message": "Refresh token expired", "status": False}
        except jwt.InvalidTokenError:
            return {"message": "Invalid refresh token", "status": False}

    def change_tier(self, email, new_tier):
        if new_tier not in ['basic', 'premium']:
            return {"message": "Invalid tier", "status": False}

        result = self.users_collection.update_one(
            {'email': email}, {"$set": {'tier': new_tier}})
        if result.matched_count > 0:
            return {"message": f"Tier updated to {new_tier}", "status": True}
        else:
            return {"message": "User not found", "status": False}

# import bcrypt
# import jwt
# from fastapi import HTTPException

# class AuthService:
#     def __init__(self, db_service):
#         self.db_service = db_service

#     def authenticate_user(self, username: str, password: str) -> str:
#         user = self.db_service.find_user_by_username(username)
#         if not user or not self.verify_password(password, user['password']):
#             raise HTTPException(status_code=401, detail="Invalid credentials")
#         return self.create_token(user)

#     def verify_password(self, plain_password: str, hashed_password: str) -> bool:
#         return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

#     def create_token(self, user: dict) -> str:
#         token = jwt.encode({"user_id": user['_id']}, "secret", algorithm="HS256")
#         return token
