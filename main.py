from fastapi import FastAPI, HTTPException, status, Depends
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import select
from sqlalchemy.orm import Session


from src.config.database import Base, engine, SessionLocal
from src.config.seed import seed

from src.routers import car_router, user_router, upload_router

@asynccontextmanager
async def lifespan(_app:FastAPI):

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
"""     try:
        seed()  
    finally:
        db.close()
    yield """




#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI(lifespan=lifespan)


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

app.include_router(
    user_router.router,
    prefix="/api/users",
    tags=["Users"]
)

app.include_router(
    upload_router.router,
    prefix="/api/upload",
    tags=["Upload"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)