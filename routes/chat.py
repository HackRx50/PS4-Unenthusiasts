from fastapi import APIRouter, HTTPException, UploadFile, File
from services.knowledgeBase import KnowledgeBaseService
from models.request_models import QueryRequest
from services.chatbot import Chatbot

chat_router = APIRouter()
knowledgebase_service = KnowledgeBaseService(collection_name="knowledge_base")
chatbot = Chatbot("chatbot")

# @chat_router.post("/addToKnowledgeBase")
# async def upload_document(file: UploadFile = File(...)):
#     return await knowledgebase_service.upsert_knowledge_base(file)
@chat_router.post("/addToKnowledgeBase")
async def upload_document(file: UploadFile = File(...)):
    try:
        print("HI")
        # Call the knowledge base service to upsert the document
        result = await knowledgebase_service.upsert_knowledge_base(file)
        
        # Return a success message with any details from the service
        return {"message": "File uploaded successfully", "details": result}
    except Exception as e:
        # Handle possible errors and return an error message
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@chat_router.post("/chat")
def search_knowledge_base(request: QueryRequest):
    result = knowledgebase_service.query_knowledge_base(request.query,request.session_id,request.document_id)
    return {"result": result}
