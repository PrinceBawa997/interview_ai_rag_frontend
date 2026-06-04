from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["register"]
collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    password: str

def hash_password(password):
    return pwd_context.hash(password)

@app.post("/register")
def user_register(user:User):

    if collection.find_one({ "username": user.username }):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)

    collection.insert_one({"username": user.username, "password":hashed_password })

    return {"message": "User created successfully"}

