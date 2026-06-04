from fastapi import FastAPI
import pymongo
from pymongo import MongoClient, collection
from pydantic import BaseModel
app = FastAPI()
client = MongoClient("mongodb://localhost:27017")
db = client["user1"]
collection=db["user_info"]


class user(BaseModel):
    user_id: int
    username: str
    sallary:int

class updateuser(BaseModel):
    username: str
    sallary: int

@app.post("/create_user")
def create_user(user: user):
    user_data = user.dict()
    user_data["isActive"] = True
    result=collection.insert_one(user_data)
    return{"massage":"user created successfully","id":str(result.inserted_id)}

@app.get("/get_user")
def get_user():
    result=list(collection.find({},{"_id":0}))
    return{"data":result}

@app.patch("/update_user")
def update_user(user_id: int,data:updateuser):
    result=collection.update_one({"user_id":user_id},{"$set":data.dict()})
    if result.modified_count == 1:
        return{"massage":"user modified successfully"}
    else:
        return{"massage":"user not modified successfully"}

@app.delete("/delete_user")
def delete_user(user_id: int):
    result=collection.update_one({"user_id":user_id},{"$set":{"isActive":False}})
    if result.modified_count==1:
        return{"massage":"user deleted successfully"}
    else:
        return{"massage":"user not deleted successfully"}



    chain = Prompt_template | llm

    class Question(BaseModel):
        topic: str

    @app.post("/ask-ai")
    def ask_ai(data: Question):
        result = chain.invoke({"topic": data.topic})

        return {
            "topic": data.topic,
            "answer": result.content
        }








