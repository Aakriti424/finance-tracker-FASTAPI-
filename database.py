from sqlmodel import create_engine, SQLModel, Session

database_name="user.db"
database_url=f"sqlite:///{database_name}"

connect_args={"check_same_thread":False}
engine=create_engine(database_url, connect_args=connect_args)

def create_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


