from pydantic import BaseModel, EmailStr
from datetime import date

class User_Create(BaseModel):
    username:str
    email:EmailStr
    password:str

class User_Read(BaseModel):
    id:int
    username:str
    email:EmailStr
    created_at:date

    
class Token(BaseModel):
    access_token:str
    token_type:str