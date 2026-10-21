from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-m3")

    def create_embedding(self, text: str):

        embedding = self.model.encode(text)

        return embedding.tolist()

    def create_embeddings(self, texts: list[str]):

        embeddings = self.model.encode(texts)

        return embeddings.tolist()