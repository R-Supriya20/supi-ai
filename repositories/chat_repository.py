from datetime import datetime, timezone
from database.mongodb import get_database


class ChatRepository:

    def __init__(self):
        db = get_database()
        self.collection = db["chat_messages"]

    def save_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str
    ):

        message = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.now(timezone.utc)
        }

        result = self.collection.insert_one(message)

        message["_id"] = result.inserted_id

        return message

    def get_messages(
        self,
        user_id: str,
        conversation_id: str
    ):

        return list(
            self.collection.find({
                "user_id": user_id,
                "conversation_id": conversation_id
            }).sort("created_at", 1)
        )