from passlib.context import CryptContext
from database import get_session
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from model import User
from datetime import timedelta, timezone, datetime
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY="561029daaaf6e8b4b8fc4a141e715f105a38172eb2e74e0863be1c694a1ea106"
ALGORITHM="HS256"
EXPIRE_DATE=15

def hash_password(plain_pw):
    return pwd_context.hash(plain_pw)

def verify_password(plain_pw, hashed_pw):
    return pwd_context.verify(plain_pw, hashed_pw)


def authenticatw_user(username:str, password:str, session:Session=Depends(get_session)):
    user=session.exec(select(User).where(User.username==username)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Invalid username or password")
    return user

def create_access_token(data:dict, expire_date:timedelta|None=None):
    to_encode=data.copy()
    if not expire_date:
        token_expire_date=datetime.now(timezone.utc)+timedelta(minutes=30)
    else:
        token_expire_date=datetime.now(timezone.utc)+expire_date
    to_encode.update({"exp":token_expire_date})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def current_user(token:str=Depends(oauth2_scheme), session:Session=Depends(get_session)):
    credential_error=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        pyload=jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        user=pyload.get("sub")
        if not user:
            raise credential_error
    except JWTError:
        raise credential_error
    user_data=session.exec(select(User).where(User.username==user))
    if not user_data:
        raise credential_error
    return user_data
    