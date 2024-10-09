from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, UploadFile, File
from routes.auth import access_data
from services.knowledgeBase import KnowledgeBaseService
from models.request_models import QueryRequest
from services.chatbot import Chatbot
from services.pineCone import VectorPineConeDatabaseService

chat_router = APIRouter()
knowledgebase_service = KnowledgeBaseService(collection_name="knowledgebase")
chatbot = Chatbot("chatbot")

# @chat_router.post("/addToKnowledgeBase")
# async def upload_document(file: UploadFile = File(...)):
#     return await knowledgebase_service.upsert_knowledge_base(file)

@chat_router.post("/addToKnowledgeBase")
async def upload_document(file: UploadFile = File(...),user_id: str = Depends(access_data)):
    try:
        print(f"User {user_id} is querying the knowledge base.")
        result = await knowledgebase_service.upsert_knowledge_base(file)
        return {"message": "File uploaded successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@chat_router.post("/chat")
def search_knowledge_base(request: QueryRequest,session_id: Optional[str] = Query(None),user_id: str = Depends(access_data)):
    try:
        print(f"User {user_id} is querying the knowledge base.")
        result = chatbot.answer(request.query, session_id, request.document_id)
        return {"result": result}
    except Exception as e:
        # Handle possible errors and return an error message
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")



