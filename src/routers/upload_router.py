from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.service.s3_service import s3_service
import uuid

from ..config.database import get_db
from src.service.auth_py import CurrentUser
from ..models.user_model import User
from ..models.user_docs_model import UserDoc
from src.schemas.user_docs_schema import DocType

router = APIRouter()

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("")
async def upload_image(
    current_user: CurrentUser,
    file: UploadFile = File(...),
    folder_name: str = "cars",
    doc_type: DocType = "doc1", 
    db: Session = Depends(get_db), 

     ):


    # Vérification du type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Format non supporté. JPEG, PNG ou WEBP uniquement.")

    contents = await file.read()

    # Vérification de la taille
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "Fichier trop volumineux. Maximum 5MB.")

    # Nom unique pour éviter les conflits
    folder = f"documents/{current_user.id}/{doc_type.value}" if folder_name == "documents" else "cars"
    filename = f"{folder}/{uuid.uuid4()}.jpg"

    url = s3_service.upload_image(contents, filename, file.content_type)

    if folder_name == "documents":
        user_doc = UserDoc(
            user_id=current_user.id,
            doc_type=doc_type,
            doc_url=filename,  # on stocke le path S3, pas l'URL signée qui expire
        )
        db.add(user_doc)
        db.commit()
        db.refresh(user_doc)

    return {"url": url, "filename": filename}


""" @router.get("/cars/{id}")
async def get_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()
    
    # Génère une URL fraîche valable 1h
    if car.image:
        car.image = s3_service.generate_url(car.image)
    
    return car """
@router.get("/{filename}")
async def get_car(
    current_user: CurrentUser, 
    filename: str,
    normal_user_email: str = "",
    doc_type: DocType = "doc1",  
    folderName: str = "cars",
    db: Session = Depends(get_db),


    ):

    if current_user.role == "admin":
        normal_user = db.execute(
            select(User).filter(User.email == normal_user_email)
        ).scalar_one_or_none()

        folder = f"documents/{normal_user.id}/{doc_type.value}" if folderName == "documents" else "cars"
        full_path = f"{folder}/{filename}"
        image_url = s3_service.generate_url(f"{full_path}")

        return image_url




    
    # Génère une URL fraîche valable 1h
    if filename != "":
        folder = f"documents/{current_user.id}/{doc_type.value}" if folderName == "documents" else "cars"
        full_path = f"{folder}/{filename}"
        image_url = s3_service.generate_url(f"{full_path}")
    
    return image_url