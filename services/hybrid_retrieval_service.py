from services.retrieval_service import RetrievalService
from repositories.chunk_repository import ChunkRepository


class HybridRetrievalService:

    def __init__(self):
        self.vector_service = RetrievalService()
        self.chunk_repository = ChunkRepository()

    def search(
        self,
        query: str,
        query_embedding: list,
        user_id: str,
        limit: int = 10
    ):
        vector_results = self.vector_service.search(
            query_embedding=query_embedding,
            user_id=user_id,
            limit=limit
        )

        keyword_results = self.chunk_repository.keyword_search(
            query=query,
            user_id=user_id,
            limit=limit
        )

        # Merge results, avoiding duplicate chunks
        merged = {}
        for chunk in vector_results + keyword_results:
            key = (
                str(chunk["document_id"]),
                chunk["text"]
            )

            if key not in merged:
                merged[key] = chunk

        return list(merged.values())[:limit]