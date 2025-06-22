from sqlmodel import SQLModel, Field, ForeignKey
from pydantic import EmailStr
from datetime import date

class User(SQLModel,table=True):
    id:int|None=Field(primary_key=True, index=True)
    created_at:date=Field(default_factory=date.today)
    username:str=Field(index=True)
    email:EmailStr=Field( unique=True)
    password:str=Field()