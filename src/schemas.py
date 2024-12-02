from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

from sqlalchemy import Column
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreateSchema(UserBase):
    password: str

class UserRetrieveSchema(UserBase):
    id: UUID
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
        
class UserUpdateSchema(BaseModel):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None






class URLShortCreateSchema(BaseModel):
    url: str

class URLShortPlanCreateSchema(BaseModel):
    url: str
    domain: str

class PlansSchema(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    duration_months: int
    
class PlansCreateSchema(BaseModel):
    name: str
    description: str
    price: float
    duration_months: int

class PlansAgreementSchema(BaseModel):
    id: UUID
    plan_id: UUID
    user_id: UUID
    start_date: datetime
    end_date: datetime

class PlansAgreementCreateSchema(BaseModel):
    plan_id: UUID


class UserLoginSchema(BaseModel):
    username: str
    password: str

