from pydantic import BaseModel, EmailStr
from uuid import UUID
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreateSchema(UserBase):
    password: str

class UserRetrieveSchema(UserBase):
    id: UUID

    class Config:
        orm_mode = True

class UserUpdateSchema(BaseModel):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None



class URLItem(BaseModel):
    url: str
