from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    conversation_id: str
    


class Source(BaseModel):
    document: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
