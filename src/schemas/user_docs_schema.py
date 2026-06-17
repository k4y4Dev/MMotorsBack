from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime




class DocType(str, Enum):
    DOC_1    = "doc1"           # En attente
    DOC_2 = "doc2"        # Traitement en cours
    DOC_3   = "doc3"          # Accepté


class DocLinkCreate(BaseModel):

    user_id: int
    doc_type: DocType
    doc_url: str
    created_at: datetime

class DocLinkResponse(DocLinkCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

