from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Query

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.schemas.car_schemas import CarCreate, CarResponse, CarUpdate, PaginatedCarsResponse
from src.schemas.filter_schemas import CarFilter
from src.models.car_model import Car
from src.config.database import Base, engine, get_db
from src.service.query_service import get_item_by_id, get_all, item_updater, item_setter, count_items, query_builder

from src.service.auth_py import CurrentUser


router = APIRouter()

@router.get("", response_model=PaginatedCarsResponse)
async def get_all_cars(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    filters: CarFilter = Depends()
    ):

    total = count_items(db, Car)
    query:str = query_builder(Car, skip, limit, filters)
    cars = get_all(db, query)

    has_more = skip + len(cars) < total

    return PaginatedCarsResponse(
        cars=[CarResponse.model_validate(car) for car in cars],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )

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

