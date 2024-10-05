from qdrant_client.http.models import PointStruct

class SemanticCacheService:
    def __init__(self, embedding_function, cache_client, cache_collection_name: str, threshold: float = 0.35):
        self.encoder = embedding_function()
        self.cache_client = cache_client
        self.cache_collection_name = cache_collection_name
        self.threshold = threshold

    def get_embedding(self, question):
        return self.encoder.embed_query(question)

    def search_cache(self, embedding):
        return self.cache_client.search(collection_name=self.cache_collection_name, query_vector=embedding, limit=1)

    def add_to_cache(self, question, response_text):
        point_id = str(uuid.uuid4())
        vector = self.get_embedding(question)
        point = PointStruct(id=point_id, vector=vector, payload={"response_text": response_text})
        self.cache_client.upsert(collection_name=self.cache_collection_name, points=[point])
