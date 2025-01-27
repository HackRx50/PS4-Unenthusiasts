from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, UploadFile, File
from routes.auth import access_data
from services.actions import ContextDatabaseService
from services.knowledgeBase import KnowledgeBaseService
from models.request_models import QueryRequest
from services.chatbot import Chatbot
from services.pineCone import VectorPineConeDatabaseService
from services.docuementProcessor import DocumentProcessor
from services.contextDatabase import ContextDatabaseService as ContextService

chat_router = APIRouter()
knowledgebase_service = KnowledgeBaseService(collection_name="knowledgebase")
document_service=DocumentProcessor()
chatbot = Chatbot("chatbot")
db_service = ContextDatabaseService()
session_service = ContextService()

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
    

@chat_router.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    try:
        # print(f"User {user_id} is querying the knowledge base.")
        result = await document_service.upload_document(file)
        print("File", file)
        return "DONE"
    except Exception as e:
        print("Error", e)
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@chat_router.post("/chat")
def search_knowledge_base(request: QueryRequest,session_id: Optional[str] = Query(None),user_id: str = Depends(access_data)):
    try:
        print(f"User {user_id} is querying the knowledge base.")
        # result, msg_id = chatbot.answer(request.query, session_id, request.document_id)
        response_data = chatbot.answer(request.query, session_id, request.document_id, user_id)
        # result = response_data.get("result")
        # msg_id = response_data.get("msg_id")
        return response_data
    except Exception as e:
        # Handle possible errors and return an error message
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@chat_router.get("/log/{message_id}")
async def get_log_status(message_id: str):
    try:
        log = db_service.get_log_by_id(message_id)  
        if log:
            return {"message_id": message_id, "output": log["output"]}
        else:
            raise HTTPException(status_code=404, detail="Log not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@chat_router.post("/reranker")
def search_knowledge_base(request: QueryRequest,session_id: Optional[str] = Query(None),user_id: str = Depends(access_data)):
    try:
        print(f"User {user_id} is querying the knowledge base.")
        # result, msg_id = chatbot.answer(request.query, session_id, request.document_id)
        response_data = chatbot.answer(request.query, session_id, request.document_id, user_id)
        # result = response_data.get("result")
        # msg_id = response_data.get("msg_id")
        return response_data
    except Exception as e:
        # Handle possible errors and return an error message
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@chat_router.get("/get_files")
def get_files():
    try:
        documents = knowledgebase_service.get_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")

    # def find_session_by_id(self, session_id: str):
    #     return self.db.sessions.find_one({"_id": session_id})


@chat_router.get("/get_chats")
def get_chats(user_id: str):
    try:
        sessions = list(session_service.find_session_by_user_id(
            user_id))
        print("Sessions", sessions)
        return {"sessions": sessions}
    except Exception as e:
        print("Error", e)
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
