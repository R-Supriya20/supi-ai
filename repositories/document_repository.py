from database.mongodb import get_database


class DocumentRepository:

    def __init__(self):
        db = get_database()
        self.collection = db["documents"]

    def create_document(self, document_data: dict):
        result = self.collection.insert_one(document_data)
        return result.inserted_id

    def find_by_id(self, document_id, user_id):
        return self.collection.find_one({
            "_id": document_id,
            "user_id": user_id
        })

    def find_by_user(self, user_id):
        return list(
            self.collection.find({
                "user_id": user_id
            })
        )

    def find_by_id_only(self, document_id):
        return self.collection.find_one({
            "_id": document_id
        })