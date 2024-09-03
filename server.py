import tempfile
import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends,Header
from PyPDF2 import PdfReader
from llama_parse import LlamaParse
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
from langchain_core.tools import StructuredTool
# import nest_asyncio

# nest_asyncio.apply()

class QueryRequest(BaseModel):
    query: str

# Load environment variables from .env file
load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
LLAMA_CLOUD_API_KEY=os.getenv("LLAMA_CLOUD_API_KEY")
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

class SemanticCache:
    def __init__(self, embedding_function, threshold=0.35):
        self.encoder = embedding_function()
        self.cache_client = qdrant_client  # Use in-memory Qdrant for cache
        self.cache_collection_name = "cache"

        # Check if the cache collection already exists, and create it if not
        collections = self.cache_client.get_collections().collections
        if not any(collection.name == self.cache_collection_name for collection in collections):
            self.cache_client.create_collection(
                collection_name=self.cache_collection_name,
                vectors_config=VectorParams(
                    size=3072,  # Assuming the output size of OpenAIEmbeddings
                    distance=Distance.EUCLID
                )
            )
            print(f"Cache collection '{self.cache_collection_name}' created.")
        else:
            print(f"Cache collection '{self.cache_collection_name}' already exists.")

        # Configure the database connection
        self.db_client = qdrant_client
        self.db_collection_name = "cache"
        self.euclidean_threshold = threshold

    def get_embedding(self, question):
        embedding = self.encoder.embed_query(question)  # Adjusted for OpenAIEmbeddings interface
        return embedding

    def search_cache(self, embedding):
        search_result = self.cache_client.search(
            collection_name=self.cache_collection_name,
            query_vector=embedding,
            limit=1
        )
        return search_result

    def add_to_cache(self, question, response_text):
        # Create a unique ID for the new point
        point_id = str(uuid.uuid4())
        vector = self.get_embedding(question)
        # Create the point with payload
        point = PointStruct(id=point_id, vector=vector, payload={"response_text": response_text})
        # Upload the point to the cache
        self.cache_client.upsert(
            collection_name=self.cache_collection_name,
            points=[point]
        )


semantic_cache = SemanticCache(embedding_function=get_embedding_function)


def search_knowledge_base(query: str, session_id: str) -> str:
    session = get_session(session_id)

    # Check semantic cache first
    query_embedding = semantic_cache.get_embedding(query)
    cache_results = semantic_cache.search_cache(query_embedding)
    
    if cache_results:
        for result in cache_results:
            if result.score <= semantic_cache.euclidean_threshold:
                print('Answer recovered from Cache.')
                print(f'Found cache with score {result.score:.3f}')
                return result.payload['response_text']

    # Cache miss: proceed with knowledge base search
    print('Cache miss. Searching knowledge base.')
    
    # Search the knowledge base in Qdrant
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,  # Convert to list for compatibility
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
    chain_input = {
        "query": query,
        "context": context,  # Pass previous session context
        "information": information
    }

    # Get the GPT response using LangChain
    gpt_response = chain.run(chain_input)

    # Add the response to the semantic cache
    semantic_cache.add_to_cache(query, gpt_response)
    
    return gpt_response



# def search_knowledge_base(query: str,session_id:str) -> str:
#     print("session_id")
    

#     session = get_session(session_id)

#     embedding_function = get_embedding_function()
#     query_embedding = embedding_function.embed_query(query)

#     # Search the knowledge base in Qdrant
#     search_result = qdrant_client.search(
#         collection_name=collection_name,
#         query_vector=query_embedding,
#         limit=5  # Return top 5 relevant results
#     )

#     # Format the results
#     results = [{"text": hit.payload["text"], "score": hit.score} for hit in search_result]

#     # Prepare the LangChain LLM chain
#     llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
#     template = ChatPromptTemplate.from_messages([
#         ("system", "You are a helpful AI assistant that answers questions based on the given information. You have to provide short and crisp answers and only provide how much information is needed."),
#         ("human", "Given the query: '{query}', the previous context: '{context}', and the following relevant information:\n{information}\nProvide a detailed answer based on the above information.")
#     ])
#     chain = LLMChain(llm=llm, prompt=template)

#     # Construct the input for LangChain, including session context
#     context = "\n".join([f"Query: {interaction['query']}\nResponse: {interaction['gpt_response']}" for interaction in session["context"]])
#     information = "\n".join([f"- {result['text']}" for result in results])
#     print(context,"CONTEXT")
#     chain_input = {
#         "query": query,
#         "context": context,  # Pass previous session context
#         "information": information
#     }

#     # Get the GPT response using LangChain
#     gpt_response = chain.run(chain_input)
#     return gpt_response
class QueryRequest(BaseModel):
    query: str
class KnowledgeBaseArgs(BaseModel):
    query: str
    session_id: str
knowledge_base_tool = StructuredTool.from_function(
    name="SearchKnowledgeBase",
    func=search_knowledge_base,
    description='Search the knowledge base for relevant information based on a detailed query from the user. ',
    args_schema=KnowledgeBaseArgs
)

todo_list = []
current_id = 1  # Start the ID count from 1

# Create a new to-do item
def add_todo_item(item: str) -> str:
    global current_id
    todo_id = current_id
    todo_list.append({"item_id": todo_id, "item": item})
    current_id += 1  # Increment the ID for the next item
    return f"Added to-do item: {item} with ID: {todo_id}"

# Read all to-do items
def list_todo_items() -> str:
    if not todo_list:
        return "Your to-do list is empty."
    return "Your to-do items are:\n" + "\n".join([f"{todo['item_id']}: {todo['item']}" for todo in todo_list])

# Update a to-do item
def update_todo_item(item_id: int,new_item:str) -> str:
    # inputs_dict = json.loads(input)
    
    todo_id = item_id
    new_item = new_item

    for todo in todo_list:
        if todo["item_id"] == todo_id:
            todo["item"] = new_item
            return f"Updated to-do item with ID: {todo_id} to: {new_item}"
    return f"No to-do item found with ID: {todo_id}"

# Delete a to-do item
def delete_todo_item(todo_id: int) -> str:
    global todo_list
    todo_list = [todo for todo in todo_list if todo["item_id"] != todo_id]
    return f"Deleted to-do item with ID: {todo_id}"

# Define tools for the to-do list CRUD operations
add_todo_tool = StructuredTool.from_function(
    name="AddToDo",
    func=add_todo_item,
    description="Add a new item to your to-do list. Input should be the to-do item."
)

list_todo_tool = StructuredTool.from_function(
    name="ListToDo",
    func=list_todo_items,
    description="List all items in your to-do list."
)
class UpdateToDoItemArgs(BaseModel):
    item_id: int
    new_item: str
update_todo_tool = StructuredTool.from_function(
    name="UpdateToDo",
    func=update_todo_item,
    description='Update an existing to-do item.',
    args_schema=UpdateToDoItemArgs,

)

delete_todo_tool = StructuredTool.from_function(
    name="DeleteToDo",
    func=lambda todo_id: delete_todo_item(int(todo_id)),
    description="Delete a to-do item. Input should be the to-do item ID."
)


# Initialize the LLM (you can continue using GPT-4)
llm = ChatOpenAI(model_name="gpt-4", api_key=OPENAI_API_KEY)

# Add the new tool to the tools list
tools = [
    knowledge_base_tool,
    add_todo_tool, list_todo_tool, update_todo_tool, delete_todo_tool
]

# Initialize the agent with the new tool
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Adjust the agent type as needed
    verbose=True
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/addToKnowledgeBase/")
async def add_to_knowledge_base(file: UploadFile = File(...)):
    # Save the uploaded file temporarily with the correct extension
    file_extension = f".{file.filename.split('.')[-1]}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    # Use LlamaParse to extract text from the document
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

        # Prepare data with unique IDs
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

    # Only upsert if there are points to insert
    if all_points:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=all_points
        )
        return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base."}
    else:
        return {"status": "error", "message": "No data extracted from the document."}


# @app.post("/addToKnowledgeBase/")
# async def add_to_knowledge_base(file: UploadFile = File(...)):
#     if file.content_type != 'application/pdf':
#         raise HTTPException(status_code=400, detail="File must be a PDF")

#     # Extract text from the PDF
#     text = extract_text_from_pdf(file)
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=20,
#         length_function=len,
#         is_separator_regex=False,
#     )

#     chunks = text_splitter.split_text(text)
#     embedding_function = get_embedding_function()
#     embeddings = embedding_function.embed_documents(chunks)

#     # Prepare data to be sent to Qdrant
#     points = [
#         PointStruct(
#             id=str(uuid.uuid4()),
#             vector=embedding,
#             payload={"text": chunk}
#         )
#         for chunk, embedding in zip(chunks, embeddings)
#     ]

#     # Insert data into Qdrant
#     qdrant_client.upsert(
#         collection_name=collection_name,
#         points=points
#     )

#     return {"status": "success", "message": f"{len(points)} pages added to knowledge base."}

@app.post("/startSession/")
async def start_session():
    session_id = create_session()
    return {"session_id": session_id}

@app.post("/chat")
async def query_knowledge_base(
    request: QueryRequest, 
    session_id: str = Header(..., alias="x-session-id"), 
    user_id: str = Header(..., alias="x-user-id")
):

    # Retrieve the session

    if not session_id or not sessions_collection.find_one({"_id": session_id}):
        # Create a new session if no valid session_id is provided
        session_id = create_session()
        print(f"New session created with ID: {session_id}")


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
