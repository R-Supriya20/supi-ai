from datetime import datetime, timezone

from repositories.document_repository import DocumentRepository
from repositories.chunk_repository import ChunkRepository

from services.document_extractor import DocumentExtractor
from services.chunking_service import ChunkingService
from services.embedding_service import EmbeddingService


class DocumentService:

    def __init__(self):

        self.document_repository = DocumentRepository()
        self.chunk_repository = ChunkRepository()

        self.extractor = DocumentExtractor()
        self.chunker = ChunkingService()
        self.embedding_service = EmbeddingService()

    def create_document(
        self,
        filename: str,
        user_id: str
    ):

        file_path = f"uploads/{filename}"

        # 1. Extract text
        text = self.extractor.extract_text(file_path)

        # 2. Create document
        document = {
            "filename": filename,
            "user_id": user_id,
            "status": "processing",
            "text": text,
            "created_at": datetime.now(timezone.utc)
        }

        document_id = self.document_repository.create_document(document)

        # 3. Create chunks
        chunks = self.chunker.create_chunks(text)

        # 4. Create embeddings
        embeddings = self.embedding_service.create_embeddings(chunks)

        # 5. Prepare chunk documents
        chunk_documents = []

        for chunk, embedding in zip(chunks, embeddings):

            chunk_documents.append({
                "document_id": document_id,
                "user_id": user_id,
                "text": chunk,
                "embedding": embedding
            })

        # 6. Store chunks
        self.chunk_repository.create_chunks(chunk_documents)

        # 7. Update status
        self.document_repository.collection.update_one(
            {"_id": document_id},
            {"$set": {"status": "processed"}}
        )

        document["id"] = str(document_id)
        document["status"] = "processed"

        return document