import os
from fastapi import APIRouter, HTTPException, Header
import jwt
from models.request_models import ChangeTierRequest, LoginRequest, RegisterRequest
from services.auth import Auth
from services.dataAccess import DataAccess
from settings import Settings
env=Settings()


JWT_SECRET = env.jwt_secret_key

auth_router = APIRouter()
auth=Auth()
data_access = DataAccess()


@auth_router.post('/register')
async def register(request: RegisterRequest):
    username = request.username
    email = request.email
    password = request.password

    # Basic validation (Pydantic ensures required fields are provided)
    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="All fields are required")
    # Call the registration logic
    result = auth.register_user(username, email, password)
    return result

@auth_router.post('/login')
async def login(request: LoginRequest):
    email = request.email
    password = request.password
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    result = auth.login_user(email, password)

    if result['status']:
        return result  # FastAPI automatically returns JSON with a 200 status code
    else:
        raise HTTPException(status_code=401, detail=result["message"])
    
@auth_router.post('/change-tier')
async def change_tier(request: ChangeTierRequest):
    result = auth.change_tier(request.email, request.tier)
    return result

def access_data(Authorization: str = Header(...)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Split the Authorization header expecting "Bearer <token>"
        parts = Authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization header format. Expected 'Bearer <token>'.")

        token = parts[1]

        # Debug print for token
        print(f"Token: {token}")

        # Decode the JWT token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(f"Decoded Token: {str(decoded_token)}")

        user_id = decoded_token.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID missing in token")

        # Debug print for user ID
        print(f"Decoded User ID: {user_id}")

        # Check data access synchronously
        result = data_access.can_access_data(user_id)
        
        if result["status"]:
            return result["user_id"]
        else:
            raise HTTPException(status_code=429, detail=result["message"])  # Rate limit reached

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

