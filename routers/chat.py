from fastapi import APIRouter, Depends

from dependencies.auth import get_current_user
from schemas.chat import ChatRequest, ChatResponse
from services.rag_service import RAGService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

rag_service = RAGService()


@router.post("", response_model=ChatResponse)
def chat(
    data: ChatRequest,
    current_user=Depends(get_current_user)
):

    result = rag_service.answer(
        question=data.question,
        user_id=str(current_user["_id"]),
        conversation_id=data.conversation_id
    )

    return result