from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")

app = FastAPI()

# Initialize the model and Qdrant client
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
qdrant_client = QdrantClient(
    url=DB_URL,
    api_key=DB_API_KEY
)

collection_name = "knowledge_base"

def extract_text_from_pdf(file: UploadFile) -> list[str]:
    """Extract text from each page of the PDF."""
    reader = PdfReader(file.file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return text

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/addToKnowledgeBase/")
async def add_to_knowledge_base(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Extract text from the PDF
    texts = extract_text_from_pdf(file)

    # Generate embeddings for each page of the PDF
    embeddings = model.encode(texts)

    # Prepare data to be sent to Qdrant
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={"text": text}
        )
        for text, embedding in zip(texts, embeddings)
    ]

    # Insert data into Qdrant
    qdrant_client.upsert(
        collection_name=collection_name,
        points=points
    )

    return {"status": "success", "message": f"{len(points)} pages added to knowledge base."}
