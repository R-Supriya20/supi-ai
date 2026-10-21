from repositories.chat_repository import ChatRepository


class ChatService:

    def __init__(self):
        self.repository = ChatRepository()

    def save_user_message(
        self,
        user_id: str,
        conversation_id: str,
        content: str
    ):

        return self.repository.save_message(
            user_id=user_id,
            conversation_id=conversation_id,
            role="user",
            content=content
        )

    def save_assistant_message(
        self,
        user_id: str,
        conversation_id: str,
        content: str
    ):

        return self.repository.save_message(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=content
        )

    def get_conversation(
        self,
        user_id: str,
        conversation_id: str
    ):

        return self.repository.get_messages(
            user_id=user_id,
            conversation_id=conversation_id
        )