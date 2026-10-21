from database.mongodb import get_database


class ChunkRepository:

    def __init__(self):
        db = get_database()
        self.collection = db["document_chunks"]

    def create_chunks(self, chunks: list):
        if chunks:
            self.collection.insert_many(chunks)

    def keyword_search(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ):
        pipeline = [
            {
                "$search": {
                    "index": "keyword_index",
                    "compound": {
                        "must": [
                            {
                                "text": {
                                    "query": query,
                                    "path": "text"
                                }
                            }
                        ],
                        "filter": [
                            {
                                "equals": {
                                    "path": "user_id",
                                    "value": user_id
                                }
                            }
                        ]
                    }
                }
            },
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "document_id": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ]

        return list(self.collection.aggregate(pipeline))