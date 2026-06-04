import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pymongo import MongoClient
from pydantic import BaseModel

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
    name:str
    template:str
@app.post("/add-prompt")
def add_prompt(data:add_prompt):
    collection.insert_one({"name":data.name, "template":data.template})
    return{"name":"prompt added successfully"}

class Question(BaseModel):
    topic:str

@app.get("/prompt")
def get_prompt():
    prompts=list(collection.find({},{"_id":0}))
    return{"prompts":prompts}

@app.post("/ask-ai/{prompt_name}")
def ask_ai(data:Question,prompt_name:str):

    prompt_data=(collection.find_one({"name":prompt_name}))
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
        "prompt_name":prompt_name,
        "topic":data.topic,
        "answer":result.content
    }


