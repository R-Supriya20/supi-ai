from services.embedding_service import EmbeddingService
from services.retrieval_service import RetrievalService
from services.prompt_service import PromptService
from services.llm_service import LLMService
from services.chat_service import ChatService
from services.query_rewriting_service import QueryRewritingService
from repositories.document_repository import DocumentRepository
from services.reranking_service import RerankingService
from services.hybrid_retrieval_service import HybridRetrievalService


class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService()
        self.prompt_service = PromptService()
        self.llm_service = LLMService()
        self.chat_service = ChatService()
        self.query_rewriting_service = QueryRewritingService()
        self.document_repository = DocumentRepository()
        self.reranking_service = RerankingService()
        self.hybrid_retrieval_service = HybridRetrievalService()

    def answer(
        self,
        question: str,
        user_id: str,
        conversation_id: str
    ):

        # 1. Save user message
        self.chat_service.save_user_message(
            user_id=user_id,
            conversation_id=conversation_id,
            content=question
        )

        # 2. Get conversation history
        conversation = self.chat_service.get_conversation(
            user_id=user_id,
            conversation_id=conversation_id
        )

        # 3. Rewrite the question
        rewritten_query = self.query_rewriting_service.rewrite(
            question=question,
            conversation=conversation
        )

        # 4. Create embedding
        query_embedding = self.embedding_service.create_embedding(
            rewritten_query
        )

        # Retrieve 10 candidate chunks
        retrieved_chunks = self.hybrid_retrieval_service.search(
            query=rewritten_query,
            query_embedding=query_embedding,
            user_id=user_id,
            limit=10
        )

        retrieved_chunks = self.reranking_service.rerank(
            question=rewritten_query,
            chunks=retrieved_chunks,
            top_k=5
        )

        # 6. Create prompt
        prompt = self.prompt_service.create_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks,
            conversation=conversation
        )

        # 7. Generate answer
        answer = self.llm_service.generate(prompt)

        # 8. Save assistant message
        self.chat_service.save_assistant_message(
            user_id=user_id,
            conversation_id=conversation_id,
            content=answer
        )

        # 9. Build sources
        sources = []

        for chunk in retrieved_chunks:

            document = self.document_repository.find_by_id_only(
                chunk["document_id"]
            )

            if document:
                sources.append({
                    "document": document["filename"],
                   "score": float(chunk["rerank_score"])
                })

        return {
            "answer": answer,
            "sources": sources
        }