

import pymongo
from fastapi import FastAPI,HTTPException,Request,Response
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
from starlette import status

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["register"]
collection = db["users"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
@app.post("/login")
def login_user(username:str,password:str):
    db_user= collection.find_one({"username": username})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password")

    if not verify_password(password,db_user["password"]):
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return{"username":f"{username} username logged in"}
