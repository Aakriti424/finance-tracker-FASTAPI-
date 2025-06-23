from pydantic import BaseModel, EmailStr
from datetime import date
from model import Transaction_type, User

class User_Create(BaseModel):
    username:str
    email:EmailStr
    password:str

class User_Read(BaseModel):
    id:int
    username:str
    email:EmailStr
    created_at:date


class Transaction_Create(BaseModel):
    title:str
    amount:int
    type:Transaction_type
    transaction_category_id:int
    notes:str

class Transaction_Read(BaseModel):
    id:int
    title:str
    amount:int
    type:Transaction_type
    transaction_category_id:int
    transaction_date:date


class Category_Create(BaseModel):
    category:str

class Category_Read(BaseModel):
    id:int
    category:str


class Token(BaseModel):
    access_token:str
    token_type:str