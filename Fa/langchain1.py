import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai



load_dotenv()

app = FastAPI()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Question(BaseModel):
    question: str

@app.post("/ask-ai")
def ask_ai(data: Question):
    response=client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=data.question
    )


    return {
        "question": data.question,
        "answer":response.text
    }