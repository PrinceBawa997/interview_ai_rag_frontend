engine =create_engine(...)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"   # or your DB URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # only for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()














import os
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["ai_data"]
collection = db["prompts"]

llm=ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")

)
class add_prompt(BaseModel):
    name: str
    template: str
@app.post("/add_prompt")
def add_prompt(data:add_prompt):
    collection.insert_one({"name":data.name, "template":data.template})
    return {"message":"Prompt added"}

@app.get("/prompt")
def get_prompt():
    prompts=list(collection.find({},{"_id":0}))
    return{"prompts":prompts}
class Question(BaseModel):
    topic:str
@app.post("/ask-ai/{prompt_name}")
def ask_ai(data:Question,prompt_name:str):

    prompt_data=collection.find_one({"name":prompt_name})
    if not prompt_data:
        return{"message":"Prompt not found"}
    template=prompt_data["template"]

    prompts_data=PromptTemplate(
        input_variables=["topic"],
        template=template

    )
    chain=prompts_data|llm

    result=chain.invoke({"topic":data.topic})

    return{
        "prompt_used":prompt_name,
        "topic":data.topic,
        "answer":result.content
    }
