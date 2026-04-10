from fastapi import FastAPI, HTTPException, status, Depends
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.schemas.car_schemas import CarCreate, CarResponse, CarUpdate
from src.models import car_model
from src.config.database import Base, engine, get_db

from src.routers import car_router

Base.metadata.create_all(bind=engine)


#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()


@app.get("/", include_in_schema=False)
def read_root():
    return {"Hello": "Test deploy CI/CD"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

app.include_router(
    car_router.router,
    prefix="/api/cars",
    tags=["Cars"]
)