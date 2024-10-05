from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    query: str
    session_id: str


