import tempfile as temp_file
from fastapi import UploadFile, File
from services.pineCone import VectorPineConeDatabaseService
from services.vectorDatabase import VectorContextDatabaseService
from services.contextDatabase import ContextDatabaseService
from services.llm import LLMService  
from services.semanicCaching import SemanticCacheService
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.openai import OpenAIEmbeddings
from llama_parse import LlamaParse
from qdrant_client.http.models import PointStruct,models
import uuid
import os
from settings import Settings

env=Settings()
OPENAI_API_KEY = env.openai_api_key
LLAMA_CLOUD_API_KEY = env.llama_cloud_api_key

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings

class KnowledgeBaseService:
    def __init__(self, collection_name: str):
        self.vector_db = VectorPineConeDatabaseService(collection_name)
        self.llm_service = LLMService()  
        self.database = ContextDatabaseService()
        self.semantic_cache = SemanticCacheService( collection_name,float(0.35))
        

    # def search_knowledge_base(self, query,document_id):
    #     cache_results = self.semantic_cache.search_cache(query)
    #     if cache_results is not None:
    #         return cache_results

    #     query_embedding = self._query_embedding(query)

    #     # Perform a filtered search by document_id before limiting the results
    #     if document_id:
    #         # Filter vectors only related to the document_id first
    #         # filter_criteria = {"must": [{"key": "document_id", "match": document_id}]}
    #         search_result = self.vector_db.search(query_embedding,limit=5,document_id=document_id)
    #     else:
    #         # If no document_id provided, perform a general search
    #         search_result = self.vector_db.search(query_embedding, limit=5)
    #     print(search_result)
    #     # If no results are found, return a message
    #     if not search_result or "matches" not in search_result or not search_result["matches"]:
    #         return "Sorry, no relevant results found for the given document."

    #     # Process the search results
    #     results = [
    #         {
    #             "text": hit["metadata"].get("text", "No text available"),
    #             "filename": hit["metadata"].get("filename", "Unknown file"),
    #             "page_number": hit["metadata"].get("page_number", "Unknown page"),
    #             "score": hit["score"]
    #         }
    #         for hit in search_result["matches"]
    #     ]

    #     # If we don't find any results after filtering, return an appropriate message
    #     if not results:
    #         return "Sorry, no relevant results found for the given document."

    #     # Concatenate the results into a formatted string
    #     information = "\n".join(
    #         [f"- {result['text']}\n  (Source: {result['filename']}, Page: {result['page_number']})" for result in results]
    #     )

    #     # Add the query to the cache for future use
    #     self.semantic_cache.add_to_cache(query, information)

    #     return information
    def search_knowledge_base(self, query, document_id):
    # Check if the query is present in the cache
        cache_results = self.semantic_cache.search_cache(query)
        if cache_results is not None:
            return cache_results

        query_embedding = self._query_embedding(query)

        # Perform a filtered search by document_id before limiting the results
        if document_id:
            search_result = self.vector_db.search(query_embedding, limit=5, document_id=document_id)
        else:
            search_result = self.vector_db.search(query_embedding, limit=5)

        print(search_result)

        # If no results are found, return a message
        if not search_result or "matches" not in search_result or not search_result["matches"]:
            return "Sorry, no relevant results found for the given document."

        # Process the search results
        results = []
        for hit in search_result["matches"]:
            metadata = hit.get("metadata", {})  # Safely get metadata, or use an empty dictionary if None
            text = metadata.get("text", "No text available")
            filename = metadata.get("filename", "Unknown file")
            page_number = metadata.get("page_number", "Unknown page")
            score = hit.get("score", 0)

            # Add the result to the list
            results.append({
                "text": text,
                "filename": filename,
                "page_number": page_number,
                "score": score
            })

        # If no results after processing, return an appropriate message
        if not results:
            return "Sorry, no relevant results found for the given document."

        # Concatenate the results into a formatted string
        information = "\n".join(
            [f"- {result['text']}\n  (Source: {result['filename']}, Page: {result['page_number']})" for result in results]
        )

        # Add the query to the cache for future use
        self.semantic_cache.add_to_cache(query, information)

        return information



        

    def query_knowledge_base(self, query: str, session_id: str = None,document_id: str = None):
        if not session_id or not self.database.find_session_by_id(session_id):
            session_id = self.database.create_session()
        # system_prompt = (
        #     "You are a helpful AI assistant that answers questions based on the given information. You have to provide short and crisp answers and only provide how much information is needed.If you don't get any relevant answer from the infromation then reply Sorry,cannot find the response in the knowledge base"
        # )
        system_prompt=(
            '''   **Note ** : If the question is not about policies and is a General messsage or greetings , answer them politely (Dont give me any policies and source), and in the end say "You can ask me about policies ,For more accurate information on genral inquiry ,you might try asking the Information Assistant—it's built specifically to sherlock the internet for you!."
              **Note ** : If information is not available, explicitly state the following message: "Sorry, I couldn't find an answer to your question in the shared policy documents. Could you please provide more details or specific context? If it's a general inquiry, you might try asking the Information Assistant—it's built specifically to sherlock the internet for you!"
                Otherwise Follow the below Instructions-
            

                Respond in a neat, readable markdown format using bullet points.
              Follow these instructions:
              - Mention source at the end of the answer (NOTE - do not mention in any other place expect the end of answer)
              - Provide page number if available (look for numbers after document names)
              - Use context if the question seems related
              - Answer only using information directly from the provided data
              - Quote directly from the data where possible
              - List out everything relevant from the provided data, give detailed answers
              - Do not provide explanations unless explicitly requested
              - Include the source or page number for any quotes or references
              - Express uncertainty if you're not sure about an answer
'''
        )
        session_data = self.database.find_session_by_id(session_id)
        context_messages = session_data.get("context", [])
        information = self.search_knowledge_base(query,document_id=document_id)
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

        return gpt_response
    
    async def upsert_knowledge_base(self, file: UploadFile = File(...)):
        document_id = str(uuid.uuid4())
        file_extension = f".{file.filename.split('.')[-1]}"
        
        # Ensure you read the file content inside the 'with' block
        content = await file.read()

        # Create a temporary file and ensure the file path is accessible
        with temp_file.NamedTemporaryFile(delete=False, suffix=file_extension) as temp:
            temp.write(content)
            temp_file_path = temp.name  # Save the temp file path
        
        # Now temp_file_path is accessible here

        parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="text")
        parsed_document = await parser.aload_data(temp_file_path)

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
                {
                'id': str(uuid.uuid4()),  # Generate unique ID for each chunk
                'values': embedding,  # Pinecone requires 'values' as the embedding
                'metadata': {  # Metadata can be any additional data
                    "text": chunk,
                    "filename": filename,
                    "page_number": page_number,
                    "chunk_index": f"{filename}_page{page_number}_chunk{chunk_index}",
                    "document_id": document_id
                    }
                 }
                for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1)
            ]
            all_points.extend(points)

        if all_points:
            self.vector_db.upsert(all_points)
            self.semantic_cache = SemanticCacheService("cache", float(0.35))
            return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base.","document_id": document_id}
        else:
            return {"status": "error", "message": "No data extracted from the document."}


    # async def upsert_knowledge_base(self, file: UploadFile = File(...)):
    #     # Extract the file extension
    #     file_extension = f".{file.filename.split('.')[-1]}"

    #     # Create a temporary file and save the file content into it
    #     with temp_file.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file_handle:
    #         content = await file.read()
    #         temp_file_handle.write(content)
    #         temp_file_path = temp_file_handle.name  # Save the temporary file path
        
    #     try:
    #         # Use the temporary file path in the document parser
    #         print("I AM HERE ")
    #         parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="text")
    #         parsed_document = parser.load_data(temp_file_path)
    #         print("I AM HERE 2 ")

    #         filename = file.filename
    #         embedding_function = get_embedding_function()
    #         all_points = []

    #         # Process each page in the document
    #         for page_number, page in enumerate(parsed_document, start=1):
    #             text_splitter = RecursiveCharacterTextSplitter(
    #                 chunk_size=800,
    #                 chunk_overlap=20,
    #                 length_function=len,
    #                 is_separator_regex=False,
    #             )

    #             chunks = [chunk for chunk in text_splitter.split_text(page.text) if chunk.strip()]
    #             if not chunks:
    #                 continue
    #             embeddings = embedding_function.embed_documents(chunks)

    #             points = [
    #                 PointStruct(
    #                     id=str(uuid.uuid4()),
    #                     vector=embedding,
    #                     payload={
    #                         "text": chunk,
    #                         "filename": filename,
    #                         "page_number": page_number,
    #                         "chunk_index": f"{filename}_page{page_number}_chunk{chunk_index}"
    #                     }
    #                 )
    #                 for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1)
    #             ]
    #             all_points.extend(points)

    #         # Upsert data into vector database if points are available
    #         if all_points:
    #             self.vector_db.upsert(all_points)
    #             self.semantic_cache = SemanticCacheService("cache", float(0.35))
    #             return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base."}
    #         else:
    #             return {"status": "error", "message": "No data extracted from the document."}
    #     finally:
    #         # Ensure the temporary file is deleted after processing
    #         os.remove(temp_file_path)

        
    def _query_embedding(self, query):
        return get_embedding_function().embed_query(query)
