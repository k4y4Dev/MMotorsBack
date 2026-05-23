from typing import Optional, Annotated
from fastapi import Query
from dataclasses import dataclass

@dataclass
class CarFilter:
    name: Annotated[Optional[str], Query()] = None
    price_max: Annotated[Optional[int], Query( ge=0)] = None
    km_max: Annotated[Optional[int], Query( ge=0)] = None