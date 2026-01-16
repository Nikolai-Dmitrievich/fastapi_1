import bcrypt
from models import (
    User,
    Token
)
from sqlalchemy import select
from dependancy import SessionDependency
from fastapi import HTTPException

def hash_password(password: str) -> str:
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password

def check_password(password: str, password_hashed: str) -> bool:
    password = password.encode()
    hashed = password_hashed.encode()
    return bcrypt.checkpw(password, hashed)
