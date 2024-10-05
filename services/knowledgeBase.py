from fastapi import UploadFile, File
from services.vectorDatabase import VectorDatabaseService
from services.database import DatabaseService
from services.llm import LLMService  
from services.semanicCaching import SemanticCacheService
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.openai import OpenAIEmbeddings
from llama_parse import LlamaParse
import uuid
import os
import tempfile as temp_file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings

class KnowledgeBaseService:
    def __init__(self, collection_name: str):
        self.vector_db = VectorDatabaseService(collection_name)
        self.llm_service = LLMService(api_key=OPENAI_API_KEY)  
        self.database = DatabaseService()
        self.semantic_cache = SemanticCacheService(get_embedding_function, self.vector_db.client, collection_name)

    def search_knowledge_base(self, query, session_id):
        if not session_id or not self.database.find_session_by_id(session_id):
            session_id = self.database.create_session()

        system_prompt = (
            "You are a helpful AI assistant that answers questions based on the given information. You have to provide short and crisp answers and only provide how much information is needed."
        )

        session_data = self.database.find_session_by_id(session_id)
        context_messages = session_data.get("context", [])

        query_embedding = self.semantic_cache.get_embedding(query)
        search_result = self.vector_db.search(query_embedding, limit=5)

        results = [{"text": hit.payload["text"], "score": hit.score} for hit in search_result]
        information = "\n".join([f"- {result['text']}" for result in results])
    
        user_prompt = f"Given the query: '{query}', and the following relevant information:\n{information}\nProvide a detailed answer based on the above information."

        messages = [{"role": "system", "content": system_prompt}]
        for message in context_messages:
            messages.append({"role": "user", "content": message["query"]})
            messages.append({"role": "assistant", "content": message["gpt_response"]})

        messages.append({"role": "user", "content": user_prompt})
        gpt_response = self.llm_service.generate_response(messages, context_messages)

        self.database.update_session_context(session_id, {
            "query": query,
            "gpt_response": gpt_response,
        })

        return {"gpt_response": gpt_response}

    async def upsert_knowledge_base(self, file: UploadFile = File(...)):
        file_extension = f".{file.filename.split('.')[-1]}"
        with temp_file.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="text")
        parsed_document = parser.load_data(temp_file_path)

        filename = file.filename
        embedding_function = get_embedding_function()
        all_points = []

        for page_number, page in enumerate(parsed_document, start=1):
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=20,
                length_function=len,
                is_separator_regex=False,
            )

            chunks = [chunk for chunk in text_splitter.split_text(page.text) if chunk.strip()]
            if not chunks:
                continue 
            embeddings = embedding_function.embed_documents(chunks)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "filename": filename,
                        "page_number": page_number,
                        "chunk_index": f"{filename}_page{page_number}_chunk{chunk_index}"
                    }
                )
                for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1)
            ]
            all_points.extend(points)

        if all_points:
            self.vector_db.upsert(all_points)
            return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base."}
        else:
            return {"status": "error", "message": "No data extracted from the document."}
