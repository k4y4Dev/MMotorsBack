from pydantic import BaseModel, ConfigDict, Field

class CarBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: int 
    km: int 
    image: str = Field(min_length=1, max_length=50)


class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    price: int | None = Field(default=None)
    km: int | None = Field(default=None)
    image: str | None = Field(default=None, min_length=1, max_length=50)
    

class CarResponse(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    #date_posted: str


class PaginatedCarsResponse(BaseModel):
    cars: list[CarResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

