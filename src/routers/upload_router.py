from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
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


""" @router.get("/cars/{id}")
async def get_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()
    
    # Génère une URL fraîche valable 1h
    if car.image:
        car.image = s3_service.generate_url(car.image)
    
    return car """
@router.get("/{filename}")
async def get_car(filename: str):

    
    # Génère une URL fraîche valable 1h
    if filename != "":
        image_url = s3_service.generate_url(f"cars/{filename}")
    
    return image_url