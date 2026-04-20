from typing import Type,TypeVar, Optional
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.config.database import Base

TSchema = TypeVar("TSchema", bound=BaseModel)
TModel = TypeVar("TModel", bound=Base)

def get_item_by_id(db: Session, model: Type[TModel], item_id: int) -> Optional[TModel]:
    query = select(model).where(model.id == item_id)
    result = db.execute(query).scalar_one_or_none()
    return result


def get_all(db: Session, model: Type[TModel] ) -> list[TModel]:
    query: str = select(model)
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