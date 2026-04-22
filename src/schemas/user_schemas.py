from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ##image_file: str | None
    ##image_path: str

class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=120)
