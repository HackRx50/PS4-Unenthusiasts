from pydantic import BaseModel
from fastapi import FastAPI, Query, Body
from typing import Optional



class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    query: str = Body(...)
    session_id: Optional[str] = Query(None)


