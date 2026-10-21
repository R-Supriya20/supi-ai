from fastapi import APIRouter, Depends
from dependencies.auth import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/test")
def admin_test(current_user=Depends(require_admin)):
    return {
        "message": "Welcome admin",
        "email": current_user["email"]
    }