from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import date
from enum import Enum
from typing import Optional, List


class User(SQLModel,table=True):
    id:int|None=Field(primary_key=True, index=True)
    created_at:date=Field(default_factory=date.today)
    username:str=Field(index=True)
    email:EmailStr=Field( unique=True)
    password:str=Field()
    transaction:List["Transaction"]=Relationship(back_populates="user")
    category:List["Transaction_Category"]=Relationship(back_populates="user")
    saving:List["Savings"]=Relationship(back_populates="user")


class Transaction_Category(SQLModel,table=True):
    id:int|None=Field(primary_key=True, index=True)
    category:str|None=Field(index=True, unique=True)
    transaction_link:List["Transaction"]=Relationship(back_populates="trans_category")
    user_id:int=Field(foreign_key="user.id")
    user:Optional[User]=Relationship(back_populates="category")


class Transaction_type(str,Enum):
    income="Income"
    expense="Expense"


class Transaction(SQLModel, table=True):
    id : int|None=Field(primary_key=True, index=True)
    user_id:int=Field(foreign_key="user.id")
    user:Optional[User]=Relationship(back_populates="transaction")
    title:str
    amount:int
    created_at:date=Field(default_factory=date.today)
    type:Transaction_type=Field(default=Transaction_type.expense,index=True)
    transaction_category_id:Optional[int]=Field(foreign_key="transaction_category.id")
    trans_category:Optional[Transaction_Category]=Relationship(back_populates="transaction_link")
    transaction_date:date=Field(default_factory=date.today)
    notes:int|None=Field(default=None)


class Savings(SQLModel, table=True):
    id:int|None=Field(primary_key=True, index=True)
    user_id:int=Field(foreign_key="user.id")
    user:Optional[User]=Relationship(back_populates="saving")
    add_amount:int
    started_at:date=Field(default_factory=date.today)
    
class fix_expenses(SQLModel,table=True):
    id:int|None=Field(primary_key=True, index=True)
    expenses_type:str=Field(index=True)
    fixed_amount:int
    created_date:date=Field(default_factory=date.today)



User.update_forward_refs()
Transaction_Category.update_forward_refs()
Transaction.update_forward_refs()
Savings.update_forward_refs()


