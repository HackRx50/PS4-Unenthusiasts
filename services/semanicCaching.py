from qdrant_client.http.models import PointStruct,VectorParams, Distance
from globals.embedding import get_embedding_function
from qdrant_client import QdrantClient
import uuid

class SemanticCacheService:
    def __init__(self, cache_collection_name: str, threshold: float = 0.70):
        self.encoder = get_embedding_function()
        self.cache_client = self._create_in_memory_cache_client()  
        self.cache_collection_name = cache_collection_name
        self.threshold:float = float(threshold)
        self._initialize_cache_collection()

    def _create_in_memory_cache_client(self):
        return QdrantClient(":memory:")  

    def _initialize_cache_collection(self):
        collections = self.cache_client.get_collections().collections
        if not any(collection.name == self.cache_collection_name for collection in collections):
            self.cache_client.create_collection(collection_name=self.cache_collection_name,vectors_config=
                     VectorParams(
                        size=3072,  
                        distance=Distance.COSINE 
                    )
                )

    def get_embedding(self, question):
        return self.encoder.embed_query(question)

    def search_cache(self, question):
        embedding = self.get_embedding(question)
        cache_results = self.cache_client.search(
            collection_name=self.cache_collection_name, 
            query_vector=embedding, 
            limit=1
        )
        print('Cache Results:', cache_results)
        if cache_results:
            for result in cache_results:
                if float(result.score) >= float(self.threshold):
                    print('Answer recovered from Cache.')
                    print(f'Found cache with score {result.score:.3f}')
                    return result.payload["text"]
        else:
            return None

    def add_to_cache(self, question, response_text):
        point_id = str(uuid.uuid4())
        vector = self.get_embedding(question)
        point = PointStruct(
            id=point_id, 
            vector=vector, 
            payload={"text": response_text}
        )
        self.cache_client.upsert(collection_name=self.cache_collection_name, points=[point])