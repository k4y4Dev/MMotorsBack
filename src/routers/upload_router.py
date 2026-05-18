from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.service.s3_service import s3_service
import uuid

from src.service.auth_py import CurrentUser

router = APIRouter()

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("")
async def upload_image(  file: UploadFile = File(...)):


    # Vérification du type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Format non supporté. JPEG, PNG ou WEBP uniquement.")

    contents = await file.read()

    # Vérification de la taille
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "Fichier trop volumineux. Maximum 5MB.")

    # Nom unique pour éviter les conflits
    filename = f"{uuid.uuid4()}.jpg"

    url = s3_service.upload_image(contents, filename, file.content_type)

    return {"url": url, "filename": filename}