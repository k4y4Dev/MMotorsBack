from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends


from sqlalchemy import select
from sqlalchemy.orm import Session

from src.schemas.car_schemas import CarCreate, CarResponse, CarUpdate
from src.models import car_model
from src.config.database import Base, engine, get_db


router = APIRouter()

@router.get("", response_model=list[CarResponse])
async def get_all_cars(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(car_model.Car))
    cars = result.scalars().all()
    return cars

@router.get("/{car_id}", response_model=CarResponse)
async def get_car(car_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(car_model.Car).where(car_model.Car.id == car_id)
    )
    car = result.scalars().first()
    if car:
        return car
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")


@router.put("/{car_id}", response_model=CarResponse)
async def update_car_full(car_id: int, car_data: CarCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(car_model.Car).where(car_model.Car.id == car_id)
    )
    car = result.scalars().first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    car.name = car_data.name
    car.price = car_data.price
    car.km = car_data.km
    car.image = car_data.image

    db.commit()
    db.refresh(car)
    return car


@router.patch("/{car_id}", response_model=CarResponse)
async def update_car_partial(car_id: int, car_data: CarUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(car_model.Car).where(car_model.Car.id == car_id)
    )
    car = result.scalars().first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    updated_data = car_data.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(car, field, value)
    


    db.commit()
    db.refresh(car)
    return car

@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(car_model.Car).where(car_model.Car.id == car_id)
    )
    car = result.scalars().first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    db.delete(car)
    db.commit()
    
@router.post(
    "",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_car(car: CarCreate, db: Annotated[Session, Depends(get_db)]):
    new_car = car_model.Car (
        name= car.name,
        price= car.price,
        km= car.km,
        image= car.image
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

