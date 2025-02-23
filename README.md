# **Pychurros 🍩**
*A lightweight, Spring JPA-style repository for FastAPI & SQLModel.*

[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-blue?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-ORM-lightgrey?style=flat&logo=python)](https://sqlmodel.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow?style=flat&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

---

## 📖 **Overview**
**Pychurros** is a dynamic and lightweight repository system for **FastAPI + SQLModel**, inspired by **Spring Data JPA**. It provides:
- ✅ **Automatic CRUD methods** (no SQL needed)
- ✅ **Dynamic queries (`find_by_*`)** based on method names
- ✅ **Full type safety & IDE auto-completion**
- ✅ **Easy integration with FastAPI & Dependency Injection**
- ✅ **Zero boilerplate repositories**

---

## 🚀 **Installation**
### **1️⃣ Install Pychurros**
```sh
pip install pychurros
```

### **2️⃣ Create a FastAPI Project**
```sh
mkdir myproject && cd myproject
touch main.py models.py repository.py
```

---

## ⚙️ **Usage**
### **1️⃣ Define Your Model**
Create a **SQLModel** entity in `models.py`:
```python
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
```

### **2️⃣ Setup Database & Repository**
```python
from sqlmodel import create_engine, Session
from pychurros import PyChurrosRepository
from models import User

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

session = Session(engine)

user_repo = PyChurrosRepository[User](session, User)
```

### **3️⃣ Using Default CRUD Methods**
```python
# Save a user
user = user_repo.save(User(name="Alice", email="alice@example.com"))

# Find user by ID
user = user_repo.find_by_id(1)

# Get all users
users = user_repo.find_all()

# Update user
user.name = "Alice Updated"
user_repo.update(user)

# Delete a user
user_repo.delete(1)

# Delete all users
user_repo.delete_all()
```

---

## 🔍 **Dynamic Query Methods (`find_by_*`)**
Pychurros automatically builds **dynamic queries** based on method names.

### **Examples**
| **Method**                           | **Query Equivalent**                                      |
|---------------------------------------|----------------------------------------------------------|
| `find_by_name("Alice")`               | `SELECT * FROM user WHERE name = 'Alice'`               |
| `find_by_email("test@example.com")`   | `SELECT * FROM user WHERE email = 'test@example.com'`   |
| `find_by_name_and_email("Alice", "test@example.com")` | `SELECT * FROM user WHERE name = 'Alice' AND email = 'test@example.com'` |

### **Example Usage**
```python
user_repo.find_by_name("Alice")
user_repo.find_by_email("test@example.com")
user_repo.find_by_name_and_email("Alice", "test@example.com")
```
- **Method names must be case-sensitive**
- **Supports `_and_` to combine multiple conditions**

---

## ⚡ **Integrating with FastAPI**
### **1️⃣ Setup Dependency Injection**
```python
from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel
from pychurros import PyChurrosRepository
from models import User
from database import engine

SQLModel.metadata.create_all(engine)

app = FastAPI()

def get_db():
    with Session(engine) as session:
        yield session

user_repo = PyChurrosRepository[User](session, User)
```

### **2️⃣ Define API Endpoints**
```python
from fastapi import FastAPI, Depends
from sqlmodel import Session
from pychurros import PyChurrosRepository
from models import User

app = FastAPI()

@app.post("/users/")
def create_user(user: User, db: Session = Depends(get_db)):
    return user_repo.save(user)

@app.get("/users/")
def get_all_users(db: Session = Depends(get_db)):
    return user_repo.find_all()

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
```

---

## 🔥 **Why Use Pychurros?**
✅ **Zero Boilerplate** - No need to write SQL queries  
✅ **Spring JPA-like Dynamic Queries** - `find_by_*` works automatically  
✅ **FastAPI & SQLModel Optimized** - Best performance & typing support  
✅ **IDE Auto-Completion** - Works with all major IDEs  
✅ **Lightweight & Simple** - No extra dependencies  

---

## 🤝 **Contributing**
We welcome contributions! Feel free to:
- Open an issue 🐛
- Submit a PR 🚀

---

## 📜 **License**
Pychurros is open-source under the [Apache 2.0 License](LICENSE).

---

## 🌟 **Support & Links**
- **FastAPI Docs**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)  
- **SQLModel Docs**: [https://sqlmodel.tiangolo.com/](https://sqlmodel.tiangolo.com/)  
- **GitHub Repository**: [https://github.com/churros-py/churros-data-ppa](https://github.com/churros-py/churros-data-ppa)  

---

## 🎉 **Happy Coding with Pychurros! 🍩**
