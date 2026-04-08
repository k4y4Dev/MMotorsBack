from fastapi import FastAPI, HTTPException, status

from schemas.car_schemas import CarCreate, CarResponse

#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()

cars: list[dict] = [
    {
        "id": 1,
        "name": "Renault",
        "price": 6500,
        "km": 95000,
    },
    {
        "id": 2,
        "name": "Mercedes",
        "price": 13800,
        "km": 195000,
    },
    {
        "id": 3,
        "name": "Opel",
        "price": 10200,
        "km": 65000,
    },
]

@app.get("/", include_in_schema=False)
def read_root():
    return {"Hello": "Test deploy CI/CD"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/api/cars", response_model=list[CarResponse])
async def get_all_cars():
    return cars

@app.get("/api/cars/{car_id}", response_model=CarResponse)
async def get_car(car_id: int):
    for car in cars:
        if car.get("id") == car_id:
            return car
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nope")
    
@app.post(
    "/api/cars",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_car(car: CarCreate):
    new_id = max(car["id"] for car in cars) + 1 if  cars else 1
    new_car = {
        "id": new_id,
        "name": car.name,
        "price": car.price,
        "km": car.km
    }

    cars.append(new_car)
    return new_car
