from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from transformers import BertTokenizer, BertModel
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, ScoredPoint,VectorParams
import uuid
import os
from dotenv import load_dotenv
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
# Load environment variables from .env file
load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")

app = FastAPI()

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=DB_URL,
    api_key=DB_API_KEY
)

collection_name = "knowledge_base"
qdrant_client.recreate_collection(
    collection_name=collection_name,
    vectors_config={"size": 768, "distance": "Cosine"}
)


def extract_text_from_pdf(file: UploadFile) -> list[str]:
    """Extract text from each page of the PDF."""
    reader = PdfReader(file.file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return text

def embed_text(text: str) -> torch.Tensor:
    """Generate embeddings for a given text using BERT."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the CLS token's embedding for the representation
    return outputs.last_hidden_state[:, 0, :].squeeze()

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
    embeddings = [embed_text(text) for text in texts]

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

@app.post("/queryKnowledgeBase/")
async def query_knowledge_base(request: QueryRequest):
    # Generate embedding for the query
    query=request.query
    print("QUERY",query)
    query_embedding = embed_text(query).tolist()

    # Search the knowledge base in Qdrant
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=5  # Return top 5 relevant results
    )

    # Format the results
    results = [{"text": hit.payload["text"], "score": hit.score} for hit in search_result]

    return {"query": query, "results": results}
