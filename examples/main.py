import logging
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from app.repository import ChurrosRepository
from sqlmodel import create_engine, Session, SQLModel, Field

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

session = Session(engine)

user_repo = ChurrosRepository[User](session, User)

app = FastAPI()

SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_repo.save(User(**user.dict()))

@app.get("/users/")
def get_all_users(db: Session = Depends(get_db)):
    return user_repo.find_all()

@app.get("/users/id/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    return user_repo.find_by_id(id)

@app.get("/users/name/{name}")
def get_users_by_name(name: str, db: Session = Depends(get_db)):
    return user_repo.find_by_name(name)

@app.get("/users/email/{email}")
def get_users_by_email(email: str, db: Session = Depends(get_db)):
    return user_repo.find_by_email(email)

@app.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    user_repo.delete(id)
    return {"message": "User deleted successfully"}

@app.delete("/users/")
def delete_all_users(db: Session = Depends(get_db)):
    user_repo.delete_all()
    return {"message": "All users deleted"}

@app.get("/users/name/{name}/email/{email}")
def get_users_by_name_and_email(name: str, email: str, db: Session = Depends(get_db)):
    return user_repo.find_by_name_and_email(name, email)
