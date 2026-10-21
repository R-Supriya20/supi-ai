from database.mongodb import get_database


class RetrievalService:

    def __init__(self):
        db = get_database()
        self.collection = db["document_chunks"]

    def search(
        self,
        query_embedding: list,
        user_id: str,
        limit: int = 5
    ):

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": limit,
                    "filter": {
                        "user_id": user_id
                    }
                }
            },
            {
                     "$project": {
                             "_id": 0,
                             "text": 1,
                             "document_id": 1,
                             "score": {"$meta": "vectorSearchScore"}
                                 }
            }
        ]

        return list(
            self.collection.aggregate(pipeline)
        )