from pydantic import BaseModel
from fastapi import FastAPI, Query, Body
from typing import List, Optional



class LoginRequest(BaseModel):
    email: str
    password: str

class QueryRequest(BaseModel):
    query: str = Body(...)
    document_id: Optional[List[str]] = Body(None)


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    phone: str
    
class ChangeTierRequest(BaseModel):
    email: str
    tier: str