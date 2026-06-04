import os
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_huggingface import data
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

llm=ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.3
)

#SAVE CURRRENT TOPIC
current_topic=""

class interview_topic(BaseModel):
    topic: str

@app.post("/topic")
def give_topic(data:interview_topic):
    global current_topic
    current_topic = data.topic

    prompt = f"""
    You are an expert interviewer.

    Topic: {data.topic}
    ask only eassy question. in starting and increase dificulty level.

    Generate only ONE interview question.
    Do not provide answer.
    """

    response=llm.invoke(prompt)

    return{
        "Topic":response.content
    }

class interview_answer(BaseModel):
    answer: str

@app.post("/reply")
def reply(data:interview_answer):
    prompt=f"""
    you are a expert interviewer.
    
    answer ={data.answer}
    Tasks:
1. Check if answer is correct.
2. Give score out of 10.
3. Explain mistakes if any.
4. Give correct answer.
5. Ask next interview question.

Format:

Score:
Feedback:
Correct Answer:
Next Question"""

    response=llm.invoke(prompt)
    return{
        "answer":response.content
    }