from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from transformers import BertTokenizer, BertModel
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams
import uuid
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class QueryRequest(BaseModel):
    query: str

# Load environment variables from .env file
load_dotenv(dotenv_path="/home/anurag/projects/chatbot/.env")

DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(DB_URL,DB_API_KEY)
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

# Create collection if it doesn't exist
def create_collection_if_not_exists():
    collections = qdrant_client.get_collections().collections
    if not any(collection.name == collection_name for collection in collections):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
        print(f"Collection '{collection_name}' created.")
    else:
        print(f"Collection '{collection_name}' already exists.")

# Call this function when the app starts
create_collection_if_not_exists()

def extract_text_from_pdf(file: UploadFile) -> list[str]:
    """Extract text from each page of the PDF."""
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text+=(page.extract_text())
    return text

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    # embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/addToKnowledgeBase/")
async def add_to_knowledge_base(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Extract text from the PDF
    text=extract_text_from_pdf(file)
    text_splitter =  text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

    chunks=text_splitter.split_text(text)
    embedding_function = get_embedding_function()
    embeddings = embedding_function.embed_documents(chunks)

    # Prepare data to be sent to Qdrant
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk}
        )
        for chunk, embedding in zip(chunks, embeddings)
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
    query = request.query
    embedding_function = get_embedding_function()
    query_embedding = embedding_function.embed_query(query)

    # Search the knowledge base in Qdrant
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=5  # Return top 5 relevant results
    )

    # Format the results
    results = [{"text": hit.payload["text"], "score": hit.score} for hit in search_result]

    # Prepare the LangChain LLM chain
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant that answers questions based on the given information. You have to provide short and crisp answers and only provide how much information is needed"),
        ("human", "Given the query: '{query}', and the following relevant information:\n{information}\nProvide a crisp answer based on the above information.")
    ])
    chain = LLMChain(llm=llm, prompt=template)

    # Construct the input for LangChain
    information = "\n".join([f"- {result['text']}" for result in results])
    chain_input = {
        "query": query,
        "information": information
    }

    # Get the GPT response using LangChain
    gpt_response = chain.run(chain_input)

    return {"query": query, "results": results, "gpt_response": gpt_response}