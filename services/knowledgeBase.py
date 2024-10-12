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
from typing import List, Optional
import uuid
import os
from settings import Settings
import time 
import cohere

env=Settings()
OPENAI_API_KEY = env.openai_api_key
LLAMA_CLOUD_API_KEY = env.llama_cloud_api_key
COHERE_API_KEY=env.cohere_api_key

co = cohere.Client(COHERE_API_KEY)

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-large",
        chunk_size=800
    )
    return embeddings

class KnowledgeBaseService:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.vector_db = VectorPineConeDatabaseService(collection_name)
        self.llm_service = LLMService()  
        self.database = ContextDatabaseService()
        self.semantic_cache = SemanticCacheService( collection_name,float(0.35))
        
        
       
        # self.create_collection()
        self.database.create_knowledgebase_collection(collection_name)
        

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
    
    def search_knowledge_base_reranker(self,query,document_id=None):
        startcache = time.time()
    # cache_results = self.semantic_cache.search_cache(query)
    # if cache_results is not None:
    #     return cache_results
        endcache = time.time()
        durationcache = endcache - startcache
        print(f"Time taken to fetch from cache: {durationcache:.4f} seconds")

        query_embedding = self._query_embedding(query)
        start_time = time.time()

        # Perform a filtered search by document_id before limiting the results
        if document_id:
            search_result = self.vector_db.searchWithFilter(query_embedding, document_id, limit=25)  # Fetch 25 chunks
        else:
            search_result = self.vector_db.search(query_embedding, limit=25)

        end_time = time.time()
        duration = end_time - start_time
        print(f"Time taken to fetch from vector database: {duration:.4f} seconds")

        util_start = time.time()

        # If no results are found, return a message
        if not search_result or "matches" not in search_result or not search_result["matches"]:
            return "Sorry, no relevant results found for the given document."

        # Process the search results
        results = []
        texts_for_rerank = []
        for hit in search_result["matches"]:
            metadata = hit.get("metadata", {})  # Safely get metadata, or use an empty dictionary if None
            text = metadata.get("text", "No text available")
            filename = metadata.get("filename", "Unknown file")
            page_number = metadata.get("page_number", "Unknown page")
            score = hit.get("score", 0)

            # Add to list for re-ranking
            texts_for_rerank.append(text)

            # Add the result to the list
            results.append({
                "text": text,
                "filename": filename,
                "page_number": page_number,
                "score": score
            })

        # If no results after processing, return an appropriate message
        print(results)
        if not results:
            return "Sorry, no relevant results found for the given document."

        # **Step: Use Cohere Re-ranking API**
        try:
            reranked_docs = co.rerank(
                query=query,
                documents=texts_for_rerank,
                top_n=len(texts_for_rerank),  # Re-rank all retrieved documents
                model="rerank-english-v2.0"
            )
            # Sort results based on the re-ranking scores
            reranked_results = sorted(
                zip(results, reranked_docs),
                key=lambda x: x[1].relevance_score,
                reverse=True
            )
            
            # Extract the top 10 sorted results based on the re-ranking
            top_10_results = [doc[0] for doc in reranked_results[:10]]
            print(top_10_results)
        except Exception as e:
            print(f"Error during re-ranking: {e}")
            top_10_results = results[:10]  # Fallback to the top 10 results from the initial search if re-ranking fails

        # Concatenate the results into a formatted string using the top 10 re-ranked results
        informationT = time.time()
        information = "\n".join(
            [f"- {result['text']}\n  (Source: {result['filename']}, Page: {result['page_number']})" for result in top_10_results]
        )

        util_end = time.time()
        duration_util = util_end - util_start
        print(f"Time taken to fetch from utils: {duration_util:.4f} seconds")
    
    # Add the query to the cache for future use
    # self.semantic_cache.add_to_cache(query, information)

        return information
        
    
    def search_knowledge_base(self, query, document_id=None):

    # Check if the query is present in the cache
        startcache=time.time()
        # cache_results = self.semantic_cache.search_cache(query)
        # if cache_results is not None:
        #     return cache_results
        endcache=time.time()
        durationcache=endcache-startcache
        print(f"Time taken to fetch from cache: {durationcache:.4f} seconds")

        query_embedding = self._query_embedding(query)
        start_time = time.time()


        # Perform a filtered search by document_id before limiting the results
        if document_id:
            search_result = self.vector_db.searchWithFilter(query_embedding, document_id,limit=5)
        else:
            search_result = self.vector_db.search(query_embedding, limit=5)

        end_time = time.time()

            # Calculate the duration
        duration = end_time - start_time
        print(f"Time taken to fetch from vector database: {duration:.4f} seconds")

        print(search_result)
        util_start=time.time();

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
        informationT=time.time()
        information = "\n".join(
            [f"- {result['text']}\n  (Source: {result['filename']}, Page: {result['page_number']})" for result in results]
        )

        util_end=time.time()
        duration_util=util_end-util_start
        print(f"Time taken to fetch from utils: {duration_util:.4f} seconds")
        # Add the query to the cache for future use
        # self.semantic_cache.add_to_cache(query, information)

        return information



        

    def query_knowledge_base(self, query: str, session_id: str = None,document_id: str = None,actual_query:str=None,context_messages:List[str]=None):
        print("HELLO")
        # system_prompt = (
        #     "You are a helpful AI assistant that answers questions based on the given information. You have to provide short and crisp answers and only provide how much information is needed.If you don't get any relevant answer from the infromation then reply Sorry,cannot find the response in the knowledge base"
        # )
        system_prompt=(
            '''   *Note * : If the question is not related to the context of the information provided dont use your knowledge to answer, stick to the knowledge base i provided, if it is out of scope then just say so to the user. Answer the question only if the question is directly within the scope of the info i provided, otherwise dont. if it is a General messsage or greetings , answer them politely
              *Note * : If query is out of context of info you have, explicitly state the following message: "Sorry, I couldn't find an answer to your question in the shared policy documents. Could you please provide more details or specific context? If it's a general inquiry, you might try asking the Information Assistant—it's built specifically to sherlock the internet for you!"
                Otherwise Follow the below Instructions-
              - Mention source at the end of the answer (NOTE - do not mention in any other place except the end of answer)
              - Provide page number if available (look for numbers after document names)
              - Use context if the question seems related
              - Answer only using information directly from the provided data
              - List out everything relevant from the provided data, give detailed answers
              - Do not provide explanations unless explicitly requested
              - Include the source or page number for any quotes or references
              - Express uncertainty if you're not sure about an answer
'''
        )
        startT=time.time();
        print("QUERY"+query)
        # information = self.search_knowledge_base(query,document_id=document_id)
        information = self.search_knowledge_base_reranker(query,document_id=document_id)
        
        endT=time.time();
        dur=endT-startT
        print(f"Time taken to fetch from knowledge base: {dur:.4f} seconds")

        user_prompt = f"Given the query: '{query}', and the following relevant information:\n{information}\nProvide a detailed answer based on the above information."
        print("HELLO1")
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context_messages)

        messages.append({"role": "user", "content": user_prompt})
        gpt_response = self.llm_service.generate_response(messages)
       


        self.database.update_session_context(session_id, {
            "query": actual_query,
            "gpt_response": gpt_response,
        })
        print("HELLO2")

        return {"gpt_response":gpt_response,"session_id":session_id}
    
    def upload_file_to_knowledge_base(self,filename,document_id,actual_filename):
        print("filename",filename)
        filePath = None
        try:
            file= open(filename, "rb") 
            filePath=file.name
        except Exception as e:
            print(f"Error in opening file {e}")
        
        if filePath is None:
            return {"status": "error", "message": "The file was not found."}
        
        try:
            parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="text")
            parsed_document =  parser.load_data(filePath)
            all_text = " ".join(page.text for page in parsed_document).strip()
            if not all_text or all_text == "NO_CONTENT_HERE":
                return {"status": "error", "message": "The document is blank or contains no meaningful text."}

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
                            "filename": actual_filename,
                            "page_number": page_number,
                            "chunk_index": f"{actual_filename}_page{page_number}_chunk{chunk_index}",
                            "document_id": document_id
                        }
                    }
                    for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1)
                ]
                all_points.extend(points)
            
            # Proceed with upserting if there are valid chunks
                print("DONE")
            if all_points:
                self.vector_db.upsert(all_points)
                self.semantic_cache = SemanticCacheService("cache", float(0.35))
                self.database.add_document_name(actual_filename,document_id=document_id,kb_name=self.collection_name)

                return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base.","document_id": document_id}
            else:
                return {"status": "error", "message": "No data extracted from the document."}
            
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
        



   




        
            



    async def upsert_knowledge_base(self, file: UploadFile = File(...)):
        document_id = str(uuid.uuid4())
        file_extension = f".{file.filename.split('.')[-1]}"
        
        # Ensure you read the file content inside the 'with' block
        content = await file.read()

        # Create a temporary file and ensure the file path is accessible
        with temp_file.NamedTemporaryFile(delete=False, suffix=file_extension) as temp:
            temp.write(content)
            temp_file_path = temp.name  # Save the temp file path
        
        # Parse the document
        parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="text")
        parsed_document = await parser.aload_data(temp_file_path)

        # Check if the document is blank or contains no meaningful text
        all_text = " ".join(page.text for page in parsed_document).strip()
        if not all_text or all_text == "NO_CONTENT_HERE":
            return {"status": "error", "message": "The document is blank or contains no meaningful text."}

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
        
        # Proceed with upserting if there are valid chunks
        if all_points:
            self.vector_db.upsert(all_points)
            self.semantic_cache = SemanticCacheService("cache", float(0.35))
            self.database.add_document_name(filename,document_id=document_id,kb_name=self.collection_name)
            return {"status": "success", "message": f"{len(all_points)} chunks added to knowledge base.","document_id": document_id}
        else:
            return {"status": "error", "message": "No data extracted from the document."}
        

        
    def _query_embedding(self, query):
        return get_embedding_function().embed_query(query)


    


