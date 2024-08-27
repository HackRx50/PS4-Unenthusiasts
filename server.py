from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from PyPDF2 import PdfReader
from transformers import BertTokenizer, BertModel
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo import MongoClient
from bson import ObjectId
import uuid
import os
from dotenv import load_dotenv
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
import json


class QueryRequest(BaseModel):
    query: str

# Load environment variables from .env file
load_dotenv(dotenv_path="/home/anurag/projects/chatbot/.env")

DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
app = FastAPI()
print("MONGO_URI",MONGO_URI)
# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]
sessions_collection = mongo_db["sessions"]

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

def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from each page of the PDF."""
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings

def create_session():
    session_id = str(ObjectId())
    sessions_collection.insert_one({"_id": session_id, "context": []})
    return session_id

def get_session(session_id: str):
    session = sessions_collection.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

def update_session(session_id: str, new_context: str):
    sessions_collection.update_one(
        {"_id": session_id},
        {"$push": {"context": new_context}}
    )

def search_knowledge_base(input: dict) -> str:
    print("session_id")
    inputs_dict = json.loads(input)
    
    query = inputs_dict.get('query')
    session_id = inputs_dict.get('session_id')

    session = get_session(session_id)

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
        ("system", "You are a helpful AI assistant that answers questions based on the given information. You have to provide short and crisp answers and only provide how much information is needed."),
        ("human", "Given the query: '{query}', the previous context: '{context}', and the following relevant information:\n{information}\nProvide a detailed answer based on the above information.")
    ])
    chain = LLMChain(llm=llm, prompt=template)

    # Construct the input for LangChain, including session context
    context = "\n".join([f"Query: {interaction['query']}\nResponse: {interaction['gpt_response']}" for interaction in session["context"]])
    information = "\n".join([f"- {result['text']}" for result in results])
    print(context,"CONTEXT")
    chain_input = {
        "query": query,
        "context": context,  # Pass previous session context
        "information": information
    }

    # Get the GPT response using LangChain
    gpt_response = chain.run(chain_input)
    return gpt_response

# Create a custom Tool for the knowledge base search
knowledge_base_tool = Tool(
    name="SearchKnowledgeBase",
    func=search_knowledge_base,
    description='Search the knowledge base for relevant information based on a detailed query from the user. '
)








# Initialize the LLM (you can continue using GPT-4)
llm = ChatOpenAI(model_name="gpt-4", api_key=OPENAI_API_KEY)

# Add the new tool to the tools list
tools = [
    knowledge_base_tool,
]

# Initialize the agent with the new tool
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Adjust the agent type as needed
    verbose=True
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/addToKnowledgeBase/")
async def add_to_knowledge_base(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Extract text from the PDF
    text = extract_text_from_pdf(file)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_text(text)
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

@app.post("/startSession/")
async def start_session():
    session_id = create_session()
    return {"session_id": session_id}

@app.post("/queryKnowledgeBase/")
async def query_knowledge_base(request: QueryRequest, session_id: str):
    # Retrieve the session

    input_text = (
        f"User has asked a Query. Answer the query from the Knowledge Base. "
        f"This is the information provided by user - "
        f"{{\"session_id\": \"{session_id}\", \"query\": \"{request.query}\"}}"
    )
    print(input_text,"INPUT TEXT")
    chain_input = {
    "query": request.query,
    "session_id": session_id,
    }

    # chain_input_str = json.dumps(chain_input)
    gpt_response = agent.run(input=input_text)

    # Update session context with the new interaction
    update_session(session_id, {"query": request.query, "gpt_response": gpt_response})

    return {"gpt_response": gpt_response}
