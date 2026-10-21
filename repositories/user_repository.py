from database.mongodb import get_database


class UserRepository:

    def __init__(self):
        db = get_database()
        self.collection = db["users"]


    def find_by_email(self, email: str):
        email = email.strip().lower()
        return self.collection.find_one({"email": email})



    def find_by_id(self, user_id):
        return self.collection.find_one({"_id": user_id})


    def create_user(self, user_data: dict):

        result = self.collection.insert_one(
            user_data
        )

        return result.inserted_id