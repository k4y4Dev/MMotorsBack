from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.schemas.car_schemas import CarCreate, CarResponse, CarUpdate
from src.models.car_model import Car
from src.config.database import Base, engine, get_db
from src.service.query_service import get_item_by_id, get_all, item_updater, item_setter

from src.service.auth_py import CurrentUser


router = APIRouter()

@router.get("", response_model=list[CarResponse])
async def get_all_cars(db: Annotated[Session, Depends(get_db)]):
    return get_all(db, Car)

@router.get("/{car_id}", response_model=CarResponse)
async def get_car(car_id: int, db: Annotated[Session, Depends(get_db)]):
    car = get_item_by_id(db, Car, car_id)
    if car:
        return car
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")


@router.put("/{car_id}", response_model=CarResponse)
async def update_car_full(car_id: int, car_data: CarCreate, current_user: CurrentUser , db: Annotated[Session, Depends(get_db)]):
    car = get_item_by_id(db, Car, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    if current_user.email != "admin1@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
    )
    item_updater(car_data, car, False)

    db.commit()
    db.refresh(car)
    return car


@router.patch("/{car_id}", response_model=CarResponse)
async def update_car_partial(car_id: int, car_data: CarUpdate, db: Annotated[Session, Depends(get_db)]):
    car = get_item_by_id(db, Car, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    item_updater(car_data, car, True)
    
    db.commit()
    db.refresh(car)
    return car

@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int,current_user: CurrentUser , db: Annotated[Session, Depends(get_db)]):

    car = get_item_by_id(db, Car, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    
    if current_user.email != "admin1@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )
    
    db.delete(car)
    db.commit()
    
@router.post(
    "",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_car(carSchema: CarCreate,current_user: CurrentUser , db: Annotated[Session, Depends(get_db)]):

    if current_user.email != "admin1@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    new_car = item_setter(carSchema, Car)

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

