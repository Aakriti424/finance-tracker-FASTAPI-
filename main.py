from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select
from database import create_database
from auth import get_session, hash_password, oauth2_scheme, verify_password,create_access_token, EXPIRE_DATE
from schemas import User_Create, User_Read, Token
from model import User
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


@app.post('/token',response_model=Token)
def login_user(input:Annotated[OAuth2PasswordRequestForm, Depends()],session:Session=Depends(get_session)):
    user=session.exec(select(User).where(User.username==input.username)).first()
    if not user or not verify_password(input.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password")
    token=create_access_token(data={"sub":user.username}, expire_date=timedelta(minutes=EXPIRE_DATE))
    return{
        "access_token":token,
        "token_type":"bearer"
    }