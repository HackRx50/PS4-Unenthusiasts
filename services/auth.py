import bcrypt
import jwt
from fastapi import HTTPException

class AuthService:
    def __init__(self, db_service):
        self.db_service = db_service

    def authenticate_user(self, username: str, password: str) -> str:
        user = self.db_service.find_user_by_username(username)
        if not user or not self.verify_password(password, user['password']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return self.create_token(user)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def create_token(self, user: dict) -> str:
        token = jwt.encode({"user_id": user['_id']}, "secret", algorithm="HS256")
        return token
