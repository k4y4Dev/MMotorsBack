from typing import Type,TypeVar, Optional, Annotated
from fastapi import Query
from sqlalchemy import select, func
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.config.database import Base
from src.schemas.filter_schemas import CarFilter

TSchema = TypeVar("TSchema", bound=BaseModel)
TModel = TypeVar("TModel", bound=Base)
TFilter = TypeVar("TFilter")

def get_item_by_id(db: Session, model: Type[TModel], item_id: int) -> Optional[TModel]:
    query = select(model).where(model.id == item_id)
    result = db.execute(query).scalar_one_or_none()
    return result


def get_all(db: Session, query: str) -> list[TModel]:
    result = db.execute(query).scalars().all()
    return result

def item_updater(schema: TSchema,item: TModel , set_item: bool = False):
    item_to_update = schema.model_dump(exclude_unset=set_item)
    for field, value in item_to_update.items():
        setattr(item, field, value)
    return item
    
def item_setter(schema: TSchema, model: TModel):
    data = schema.model_dump()
    new_item = model(**data)
    return new_item

def query_builder( 
    model: Type[TModel],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 1,
    filters: Optional[TFilter] = None,
    ) -> str:
    query = select(model).offset(skip).limit(limit)

    if not filters:
        return query

    if isinstance(filters, CarFilter):
        if filters.name is not None:
            query = query.where(model.name.ilike(f"%{filters.name}%"))
        if filters.price_max is not None:
            query = query.where(model.price <= filters.price_max)
        if filters.km_max is not None:
            query = query.where(model.km <= filters.km_max)
        if filters.trade is not None:
            query = query.where(model.trade == filters.trade)
    return query

def count_items(db: Session, model: Type[TModel], filters: Optional[TFilter] = None,):
    query = select(model)
    if isinstance(filters, CarFilter):
        if filters.name is not None:
            query = query.where(model.name.ilike(f"%{filters.name}%"))
        if filters.price_max is not None:
            query = query.where(model.price <= filters.price_max)
        if filters.km_max is not None:
            query = query.where(model.km <= filters.km_max)
        if filters.trade is not None:
            query = query.where(model.trade == filters.trade)
    count_result = db.execute(select(func.count()).select_from(query))
    total = count_result.scalar() or 0
    return total
