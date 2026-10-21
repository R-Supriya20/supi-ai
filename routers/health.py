from fastapi import APIRouter, Depends
from schemas.health import HealthResponse
from dependencies.common import get_db


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("", response_model=HealthResponse)
def health_check():

    return {
        "status": "ok",
        "service": "AI Customer Support Backend"
    }


@router.get("/db")
def database_health(db=Depends(get_db)):

    db.command("ping")

    return {
        "status": "ok",
        "database": "connected"
    }