from pydantic import BaseModel, ConfigDict, Field

class CarBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: int 
    km: int 


class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    model_config = ConfigDict(fron_attributes=True)

    id: int
    #date_posted: str

