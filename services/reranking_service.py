from sentence_transformers import CrossEncoder


class RerankingService:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        question: str,
        chunks: list,
        top_k: int = 5
    ):
        if not chunks:
            return []

        pairs = [
            [question, chunk["text"]]
            for chunk in chunks
        ]

        scores = self.model.predict(pairs)

        ranked_chunks = []

        for chunk, score in zip(chunks, scores):
            ranked_chunk = chunk.copy()
            ranked_chunk["rerank_score"] = float(score)
            ranked_chunks.append(ranked_chunk)

        ranked_chunks.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return ranked_chunks[:top_k]