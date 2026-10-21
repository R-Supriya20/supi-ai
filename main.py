from fastapi import FastAPI

from config.settings import settings
from routers.health import router as health_router

from middleware.request_id import RequestIDMiddleware

from exceptions.handlers import (AppException,app_exception_handler)

from routers.auth import router as auth_router
from routers.admin import router as admin_router

from routers.documents import router as documents_router

from app_logging.logger import setup_logging

from services.embedding_service import EmbeddingService
from services.retrieval_service import RetrievalService
from dependencies.auth import get_current_user
from fastapi import Depends

from routers.chat import router as chat_router

from fastapi.middleware.cors import CORSMiddleware



embedding_service = EmbeddingService()
retrieval_service = RetrievalService()



logger = setup_logging()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware
app.add_middleware(
    RequestIDMiddleware
)


# Exception handlers
app.add_exception_handler(
    AppException,
    app_exception_handler
)


# Routers
app.include_router(health_router)

app.include_router(auth_router)

app.include_router(admin_router)

app.include_router(documents_router)

app.include_router(chat_router)

@app.get("/")
def root():

    return {
        "message": "AI Customer Support Backend is running"
    }

@app.get("/test-search")
def test_search(
    question: str,
    current_user=Depends(get_current_user)
):

    query_embedding = embedding_service.create_embedding(question)

    results = retrieval_service.search(
        query_embedding=query_embedding,
        user_id=str(current_user["_id"]),
        limit=5
    )

    return {
        "question": question,
        "results": results
    }