from fastapi import FastAPI, Depends, HTTPException, status
from calendar import monthrange
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from typing import Annotated, List
from sqlmodel import Session, select,func
from database import create_database
from auth import get_session, hash_password, oauth2_scheme, verify_password,create_access_token, EXPIRE_DATE, current_user
from schemas import User_Create, User_Read, Token, Transaction_Create, Transaction_Read, Category_Create, Category_Read, Savings_Create, Savings_Read,Savings_add_amount, History_filter
from model import User, Transaction, Transaction_Category, Savings
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
import os
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import FileResponse
import io

app=FastAPI()

@app.on_event("startup")
def on_startup():
    create_database()


@app.post('/register', response_model=User_Read, tags=["User"])
def register_user(input:User_Create,session:Session=Depends(get_session)):
    try:
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
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="This email is already registered in our system")
    


@app.post('/token',response_model=Token, tags=["User"])
def login_user(input:Annotated[OAuth2PasswordRequestForm, Depends()],session:Session=Depends(get_session)):
    user=session.exec(select(User).where(User.username==input.username)).first()
    if not user or not verify_password(input.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password")
    token=create_access_token(data={"sub":user.username}, expire_date=timedelta(minutes=EXPIRE_DATE))
    return{
        "access_token":token,
        "token_type":"bearer"
    }


@app.post('/transaction', response_model=Transaction_Read, tags=["Transaction"])
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

@app.get('/transaction/{id}',response_model=Transaction_Read, tags=["Transaction"])
def get_a_transaction(transaction_id:int=id, session:Session=Depends(get_session), user:User=Depends(current_user)):
    transaction=session.exec(select(Transaction).where(Transaction.id==transaction_id)).first()
    if transaction.user_id==user.id:
        return transaction
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have a transaction in this id")


@app.get('/transaction',tags=["Transaction"])
def get_all_transactions(user:User=Depends(current_user), session:Session=Depends(get_session)):
    transactions=session.exec(select(Transaction).where(Transaction.user_id==user.id)).all()
    return transactions

@app.delete('/transaction/{id}',tags=["Transaction"])
def delete_transaction(transaction_id:int=id, session:Session=Depends(get_session), user:User=Depends(current_user)):
    transaction=session.exec(select(Transaction).where(Transaction.id==transaction_id)).first()
    if transaction.user_id==user.id:
        session.delete(transaction)
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Deleted successfully")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")


@app.post('/category', response_model=Category_Read, tags=["Category"])
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
    

@app.get('/cetgory', tags=["Category"])
def get_all_categories(session:Session=Depends(get_session), user:User=Depends(current_user)):
    category=session.exec(select(Transaction_Category).where(Transaction_Category.user_id==user.id)).all()
    return category

@app.delete('/category/{id}',tags=["Category"])
def delete_category(category_id:int=id,session:Session=Depends(get_session),user:User=Depends(current_user)):
    category=session.exec(select(Transaction_Category).where(Transaction_Category.id==category_id)).first()
    if category.user_id==user.id:
        session.delete(category)
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Successfully Deleted")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")


@app.post('/savings', response_model=Savings_Read, tags=["Savings"])
def create_savings(input:Savings_Create, session:Session=Depends(get_session), user:User=Depends(current_user)):
    savings_db=Savings(
        user_id=user.id,
        goal=input.goal,
        add_amount=input.add_amount
    )
    session.add(savings_db)
    session.commit()
    session.refresh(savings_db)
    return savings_db



@app.post('/add amount/{id}', tags=["Savings"])
def add_amount(input:Savings_add_amount,savings_id:int=id, session:Session=Depends(get_session), user:User=Depends(current_user)):
    saving=session.exec(select(Savings).where(Transaction.id==savings_id)).first()
    
    if saving.user_id==user.id:
        saving_db=Savings(
            user_id=user.id,
            add_amount=saving.add_amount
        )
        session.add(saving_db)
        session.commit()
        session.refresh(saving_db)
        total=session.exec(select(func.sum(Savings.add_amount)).where(Savings.user_id==user.id)).one()
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail=f"Price {input.amount} has been added to your savings. Total : {total}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")



@app.post("/saving history",tags=["Savings"])
def filter_saving_history(input:History_filter,session: Session = Depends(get_session), user: User = Depends(current_user)):
    month=input.time.month
    year=input.time.year

    start_date=date(year, month, 1)
    end_day=monthrange(year, month)[1]
    end_date=date(year, month, end_day)
    
    
    history = session.exec(select(Savings)
                           .where(Savings.user_id == user.id)
                           .where(Savings.started_at>=start_date)
                           .where(Savings.started_at<=end_date)).all()
    if not history:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    total=session.exec(select(func.sum(Savings.add_amount)).where(Savings.user_id==user.id)
                                                            .where(Savings.started_at>=start_date)
                                                            .where(Savings.started_at<=end_date)).one()
    data_list = [
        {
            "added_amount": i.add_amount,
            "saved_at": i.started_at
        }
        for i in history
    ]

    return {
        "data": data_list,
        "total": total
    }

@app.get("/saving history",tags=["Savings"])
def view_all_history(session:Session=Depends(get_session), user:User=Depends(current_user)):
    history=session.exec(select(Savings).where(Savings.user_id==user.id)).all()
    total=session.exec(select(func.sum(Savings.add_amount)).where(Savings.user_id==user.id)).one()
    history_list=[
        {
            "added_amount":i.add_amount,
            "saved_at":i.started_at
        }for i in history
    ]
    return{
        "data":history_list,
        "total":total
    }


templates=Environment(loader=FileSystemLoader("templates"))


@app.post("/monthly report", tags=["Monthly Report"])
def genereate_report(input:History_filter,session:Session=Depends(get_session), user:User=Depends(current_user)):
    month=input.time.month
    year=input.time.year

    start_date=date(year, month, 1)
    end_day=monthrange(year, month)[1]
    end_date=date(year, month, end_day)
    
    user_rn=session.get(User, user.id)
    income=session.exec(select(func.sum(Transaction.amount)).where(Transaction.user_id==user.id)
                        .where(Transaction.type=="Income")
                        .where(Transaction.created_at>=start_date)
                        .where(Transaction.created_at<=end_date)).one()
    expense=session.exec(select(func.sum(Transaction.amount)).where(Transaction.user_id==user.id)
                    .where(Transaction.type=="Expense")
                    .where(Transaction.created_at>=start_date)
                    .where(Transaction.created_at<=end_date)).one()
    savings=session.exec(select(func.sum(Savings.add_amount)).where(Savings.user_id==user.id)
                    .where(Savings.started_at>=start_date)
                    .where(Savings.started_at<=end_date)).one()
    data={
        "user":user_rn.username,
        "month":month,
        "income":income,
        "expense":expense,
        "savings":savings
    }
    
    template=templates.get_template("report.html")
    html_content=template.render(**data)
    file_path="monthly_report.pdf"
    HTML(string=html_content).write_pdf(file_path)

    return FileResponse(path=file_path, media_type="application/pdf", filename="Monthly_Report.pdf")