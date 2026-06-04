import pymongo
from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["student"]
collection = db["student"]
filter={"name":"prince"}
update={"age":"100"}
collection.update_one(filter,{"$set":update})
delete_data={"name":"prinxesf"}
collection.delete_one(delete_data)


class Student(BaseModel):
    name: str
    age: int
    rollnumber: int
@app.post("/student_info")
def get_student_info(student: Student):
    result= collection.insert_one(student.dict())
    return{"massage":"add user information is done",  "id": str(result.inserted_id)}






