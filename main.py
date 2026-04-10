from fastapi import FastAPI, HTTPException, status, Depends
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.schemas.car_schemas import CarCreate, CarResponse, CarUpdate
from src.models import car_model
from src.config.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)


#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()


@app.get("/", include_in_schema=False)
def read_root():
    return {"Hello": "Test deploy CI/CD"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/api/cars", response_model=list[CarResponse])
async def get_all_cars(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(car_model.Car))
    cars = result.scalars().all()
    return cars

@app.get("/api/cars/{car_id}", response_model=CarResponse)
async def get_car(car_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(car_model.Car).where(car_model.Car.id == car_id)
    )
    car = result.scalars().first()
    if car:
        return car
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")


@app.put("/api/cars/{car_id}", response_model=CarResponse)
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

    db.commit()
    db.refresh(car)
    return car


@app.patch("/api/cars/{car_id}", response_model=CarResponse)
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

@app.delete("/api/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(car_model.Car).where(car_model.Car.id == car_id)
    )
    car = result.scalars().first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    db.delete(car)
    db.commit()
    
@app.post(
    "/api/cars",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_car(car: CarCreate, db: Annotated[Session, Depends(get_db)]):
    new_car = car_model.Car (
        name= car.name,
        price= car.price,
        km= car.km
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

