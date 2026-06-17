from pydantic import BaseModel, ConfigDict, EmailStr, Field
from src.schemas.user_docs_schema import DocLinkResponse

class UserBase(BaseModel):
    email: EmailStr = Field(max_length=120)
    lastname: str = Field(max_length=120)
    firstname: str = Field(max_length=120)
    role: str = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ##image_file: str | None
    ##image_path: str

class UserPrivate(BaseModel):
    email: EmailStr
    lastname: str = Field(max_length=120)
    firstname: str = Field(max_length=120)
    role: str = Field(max_length=120)

class LoginResponseModel(BaseModel):
    message: str
    user: UserPrivate


class UserUpdate(BaseModel):
    email: EmailStr = Field(max_length=120)
    lastname: str = Field(max_length=120)
    firstname: str = Field(max_length=120)
    role: str = Field(max_length=120)

class UserCaseResponse(BaseModel):
    email: EmailStr
    lastname: str = Field(max_length=120)
    firstname: str = Field(max_length=120)

class UserCaseResponseProfile(BaseModel):
    
    id: int
    email: EmailStr = Field(max_length=120)
    lastname: str = Field(max_length=120)
    firstname: str = Field(max_length=120)
    role: str = Field(max_length=120)
    doc_links: list[DocLinkResponse] = []