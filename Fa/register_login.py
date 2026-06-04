from fastapi import FastAPI, HTTPException,Request,Response,Depends,status
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["register_login"]
collection = db["users"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

@app.post("/register_user")
def register_user(username:str,password:str):

    if collection.find_one({"username": username}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    hashed_password=hash_password(password)
    collection.insert_one({"username": username, "password": hashed_password })

    return {"message": "User created successfully"}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/login_user")
def login_user(username,password:str):

    db_user=collection.find_one({"username": username})

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User does not exist")
    if not verify_password(password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Incorrect Password")

    return {"message": "Login successful"}