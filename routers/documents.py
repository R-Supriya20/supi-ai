from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from dependencies.auth import get_current_user
from services.document_service import DocumentService
from schemas.document import DocumentResponse
import os


router = APIRouter(prefix="/documents", tags=["Documents"])

document_service = DocumentService()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    content = await file.read()

    with open(file_path, "wb") as output_file:
        output_file.write(content)

    document = document_service.create_document(
        filename=file.filename,
        user_id=str(current_user["_id"])
    )

    return document