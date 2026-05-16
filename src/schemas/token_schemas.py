from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Token(BaseModel):

    access_token: str
    token_type: str