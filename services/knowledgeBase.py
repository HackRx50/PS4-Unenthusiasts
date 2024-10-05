from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from fastapi import APIRouter, UploadFile, File
from langchain_community.embeddings.openai import OpenAIEmbeddings
from llama_parse import LlamaParse
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")
LLAMA_CLOUD_API_KEY=os.getenv("LLAMA_CLOUD_API_KEY")

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings


class KnowledgeBaseService:
    def __init__(self,collection_name: str):
        self.client = QdrantClient(
                url=DB_URL,
                api_key=DB_API_KEY
            )
        self.collection_name = collection_name
        self.create_collection()
        

    def create_collection(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(collection_name=self.collection_name)

    def search_knowledge_base(self, query_vector, limit: int = 5):
        return self.client.search(collection_name=self.collection_name, query_vector=query_vector, limit=limit)

    async def upsert_knowledge_base(self,file: UploadFile = File(...)):
    
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
            self.client.upsert(
                collection_name=self.collection_name,
                points=all_points
            )
            return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base."}
        else:
            return {"status": "error", "message": "No data extracted from the document."}




        
