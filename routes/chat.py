from fastapi import APIRouter, UploadFile, File
from services.knowledgeBase import KnowledgeBaseService
from models.request_models import QueryRequest


chat_router = APIRouter()
knowledgebase_service = KnowledgeBaseService(collection_name="knowledge_base")

@chat_router.post("/addToKnowledgeBase")
async def upload_document(file: UploadFile = File(...)):
    return knowledgebase_service.upsert_knowledge_base(file)

@chat_router.post("/chat")
def search_knowledge_base(request: QueryRequest):
    result = knowledgebase_service.search_knowledge_base(request.query,request.session_id)
    return {"result": result}
