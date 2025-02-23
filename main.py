from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import re
from typing import Type, TypeVar, List
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

T = TypeVar("T", bound=Base)

def Repository(cls):
    cls._is_repository = True
    return cls

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

class GenericRepository:
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def _generate_query(self, method_name: str, *args) -> List[T]:
        pattern = r"find_by_(\w+)"
        match = re.match(pattern, method_name)

        if not match:
            raise AttributeError(f"Method '{method_name}' is not recognized")

        field_names = match.group(1).split("_and_")
        
        if len(field_names) != len(args):
            raise ValueError(f"Method '{method_name}' expects {len(field_names)} parameters, but got {len(args)}")

        filters = [getattr(self.model, field) == value for field, value in zip(field_names, args)]
        
        query = self.session.query(self.model).filter(*filters)
        
        result = query.all()

        print(f"🔍 Executing Query: {query}")  
        print(f"🔍 Query Result: {result}")  

        return result or []  

    def __getattr__(self, name: str):
        print(f"🔍 Intercepting method call: {name}")  # Debugging

        if name.startswith("find_by_"):
            def method(*args):
                return self._generate_query(name, *args)
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

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
