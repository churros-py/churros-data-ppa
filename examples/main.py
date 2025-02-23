from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import logging
from app.repository.decorators import Repository
from app.repository.base import GenericRepository

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

@Repository
class UserRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session, User)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/name/{name}")
def get_users_by_name(name: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    users = user_repo.find_by_name(name)
    print(f"🔍 Retrieved users: {users}")
    return users

@app.get("/users/email/{email}")
def get_users_by_email(email: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return user_repo.find_by_email(email)

@app.get("/users/id/{id}")
def get_users_by_id(id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return user_repo.find_by_id(id)

@app.get("/users/name/{name}/email/{email}")
def get_users_by_name_and_email(name: str, email: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return user_repo.find_by_name_and_email(name, email)
