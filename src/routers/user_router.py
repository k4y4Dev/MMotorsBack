from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import func, select

from src.schemas.user_schemas import UserCreate, UserPublic, UserUpdate, UserPrivate, LoginResponseModel
from src.schemas.token_schemas import Token
from src.models.user_model import User
from src.config.database import Base, engine, get_db
from config import settings
from src.service.query_service import get_item_by_id, get_all, item_updater, item_setter

from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm

from src.service.auth_py import create_access_token, hash_password, oauth2_scheme, verify_access_token, verify_password, CurrentUser


router = APIRouter()

@router.get("", response_model=list[UserPublic])
async def get_all_users(db: Annotated[Session, Depends(get_db)]):
    return get_all(db, User)

""" @router.get("/me", response_model=UserPrivate)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    ""Get the currently authenticated user.""
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate user_id is a valid integer (defense against malformed JWT)
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = db.execute(
        select(User).where(User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user """


""" 2nd version """
@router.get("/me", response_model=UserPrivate)
async def get_current_user(
    current_user:CurrentUser
):
    return current_user



@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = get_item_by_id(db, User, user_id)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

@router.put("/{user_id}", response_model=UserPrivate)
async def update_user_full(user_id: int, user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    user = get_item_by_id(db, User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    item_updater(user_data, user, False)

    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user_partial(user_id: int, user_data: UserUpdate, db: Annotated[Session, Depends(get_db)]):
    user = get_item_by_id(db, User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    item_updater(user_data, user, True)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser, 
    db: Annotated[Session, Depends(get_db)]):



    user = get_item_by_id(db, User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    if current_user.email not in ('admin1@gmail.com', 'admin2@gmail.com'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )
    
    db.delete(user)
    db.commit()
    
""" @router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED
)
async def create_user(userSchema: UserCreate, db: Annotated[Session, Depends(get_db)]):
    new_user = item_setter(userSchema, User)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user """

@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(User).where(func.lower(User.email) == user.email.lower()),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=user.email.lower(),
        password_hashed=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token", response_model=LoginResponseModel)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    response: Response
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = db.execute(
        select(User).where(
            func.lower(User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    expire_date = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    max_age_seconds = settings.access_token_expire_minutes * 360

    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        expires=expire_date,
        max_age=max_age_seconds,
        domain="localhost"
        
    )
    return {
        "message": f"Bienvenue {user.email}",
        "user": {
            "email": user.email
        }
    }