import pymongo
from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel



app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["ai_data"]
collection = db["user"]
class user(BaseModel):
    name: str
    age: int
db = client["user"]
collection = db["user"]


@app.post("/add_user")

def add_user(user: user):
    user=collection.insert_one(user.dict())
    return{"message":"User added successfully"}
