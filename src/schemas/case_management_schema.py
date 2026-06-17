# case_management_schema.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from src.schemas.car_schemas import CarResponse
from src.schemas.user_schemas import UserCaseResponse
from src.schemas.user_docs_schema import DocLinkResponse

class CaseStatus(str, Enum):
    PENDING    = "pending"           # En attente
    PROCESSING = "processing"        # Traitement en cours
    APPROVED   = "approved"          # Accepté
    REFUSED    = "refused"           # Refusé

class CaseManagementCreate(BaseModel):

    car_id: int

class CaseManagementUpdate(BaseModel):
    status: CaseStatus

class CaseManagementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    car: CarResponse
    status: CaseStatus
#    doc_links: list[DocLinkResponse]
    created_at: datetime
    updated_at: datetime

class AdminCaseManagementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: UserCaseResponse
    car: CarResponse
    status: CaseStatus
    created_at: datetime
    updated_at: datetime

class CaseUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    case_id: int
    email: str
    lastname: str
    firstname: str
    status: CaseStatus
    doc_links: list[DocLinkResponse]
    created_at: datetime

class CarCaseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    car: CarResponse
    pending_count: int
    cases: list[CaseUserSummary]