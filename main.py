from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from sqlmodel import Session, select
from database import create_database
from auth import get_session, hash_password, oauth2_scheme, verify_password,create_access_token, EXPIRE_DATE, current_user
from schemas import User_Create, User_Read, Token, Transaction_Create, Transaction_Read, Category_Create, Category_Read
from model import User, Transaction, Transaction_Category
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm



app=FastAPI()

@app.on_event("startup")
def on_startup():
    create_database()


@app.post('/register', response_model=User_Read, tags=["User"])
def register_user(input:User_Create,session:Session=Depends(get_session)):
    hashed_pw=hash_password(input.password)
    user_db=User(
        username=input.username,
        email=input.email,
        password=hashed_pw
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@app.post('/token',response_model=Token, tags=["Login"])
def login_user(input:Annotated[OAuth2PasswordRequestForm, Depends()],session:Session=Depends(get_session)):
    user=session.exec(select(User).where(User.username==input.username)).first()
    if not user or not verify_password(input.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password")
    token=create_access_token(data={"sub":user.username}, expire_date=timedelta(minutes=EXPIRE_DATE))
    return{
        "access_token":token,
        "token_type":"bearer"
    }


@app.post('/transaction', response_model=Transaction_Read, tags=["Create Transaction"])
def created_transaction(input:Transaction_Create, current_user:User= Depends(current_user),session:Session=Depends(get_session)):
    transaction_db=Transaction(
        user_id=current_user.id,
        title=input.title,
        amount=input.amount,
        type=input.type,
        transaction_category_id=input.transaction_category_id,
        notes=input.notes
    )
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)
    return transaction_db

@app.get('/transaction/{id}',response_model=Transaction_Read, tags=["View A Transaction"])
def get_a_transaction(transaction_id:int=id, session:Session=Depends(get_session), user:User=Depends(current_user)):
    transaction=session.exec(select(Transaction).where(Transaction.id==transaction_id)).first()
    if transaction.user_id==user.id:
        return transaction
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have a transaction in this id")


@app.get('/transaction',tags=["View All Transaction"])
def get_all_transactions(user:User=Depends(current_user), session:Session=Depends(get_session)):
    transactions=session.exec(select(Transaction).where(Transaction.user_id==user.id)).all()
    return transactions

@app.delete('/transaction/{id}',tags=["Delete Transaction"])
def delete_transaction(transaction_id:int=id, session:Session=Depends(get_session), user:User=Depends(current_user)):
    transaction=session.exec(select(Transaction).where(Transaction.id==transaction_id)).first()
    if transaction.user_id==user.id:
        session.delete(transaction)
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Deleted successfully")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")


@app.post('/category', response_model=Category_Read, tags=["Create Category"])
def create_category(input:Category_Create, session:Session=Depends(get_session), user:User=Depends(current_user)):
    category_db=Transaction_Category(
        category=input.category,
        user_id=user.id
    )
    try:
        session.add(category_db)
        session.commit()
        session.refresh(category_db)
        return category_db
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="This category is already created")
    

@app.get('/cetgory', tags=["View all categories"])
def get_all_categories(session:Session=Depends(get_session), user:User=Depends(current_user)):
    category=session.exec(select(Transaction_Category).where(Transaction_Category.user_id==user.id)).all()
    return category

@app.delete('/category/{id}',tags=["Delete Category"])
def delete_category(category_id:int=id,session:Session=Depends(get_session),user:User=Depends(current_user)):
    category=session.exec(select(Transaction_Category).where(Transaction_Category.id==category_id)).first()
    if category.user_id==user.id:
        session.delete(category)
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Successfully Deleted")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")