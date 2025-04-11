from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class BlogCreate(BaseModel):
    
    title: str
    content: str

class BlogOut(BaseModel):
    id: int
    owner_id: int
    title: str
    content: str

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str