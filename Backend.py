import os
from fastapi import FastAPI, UploadFile, File
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# =========================
# LLM
# =========================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# =========================
# GLOBAL EMBEDDING (FIXED)
# =========================
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

embedding = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"

)

# =========================
# INTERVIEW AI
# =========================
class RequestTopic(BaseModel):
    topic: str

class RequestAnswer(BaseModel):
    Answer: str

current_topic = ""

@app.post("/topic")
async def topic(data: RequestTopic):
    global current_topic
    current_topic = data.topic

    prompt = f"""
Ask only easy interview questions at first and increase difficulty gradually.

Topic: {data.topic}

Generate ONLY ONE interview question.
Do not provide answer.
"""

    response = llm.invoke(prompt)

    question = response.content
    if isinstance(question, list):
        question = question[0]["text"]

    return {"topic": question}


@app.post("/answer")
async def answer(data: RequestAnswer):
    global current_topic

    prompt = f"""
You are an expert interviewer.

Answer = {data.Answer}

Tasks:
1. Check if answer is correct
2. Give score out of 10
3. Explain mistakes
4. Give correct answer
5. Ask next question

Format:
Score:
Feedback:
Correct Answer:
Next Question:
"""

    response = llm.invoke(prompt)

    result = response.content
    if isinstance(result, list):
        result = result[0]["text"]

    return {"Answer": result}


# =========================
# RAG SYSTEM
# =========================
vectorstore = None


@app.post("/pdf")
async def read_pdf(file: UploadFile = File(...)):
    global vectorstore

    try:
        contents = await file.read()

        file_path = f"temp_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(contents)

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        text = " ".join([doc.page_content for doc in documents])

        words = text.split()

        chunk_size = 100
        chunk_overlap = 10
        chunks = []

        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = words[i:i + chunk_size]
            chunks.append(" ".join(chunk))

        vectorstore = FAISS.from_texts(chunks, embedding)

        os.remove(file_path)

        return {"message": "file uploaded successfully"}

    except Exception as e:
        return {"error": str(e)}


# =========================
# ASK FROM PDF
# =========================
class Question(BaseModel):
    question: str


@app.post("/ask")
async def ask(data: Question):

    global vectorstore

    try:

        if vectorstore is None:
            return {"error": "Upload PDF first"}

        docs = vectorstore.similarity_search(
            data.question,
            k=5
        )

        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are a smart AI assistant.

Answer ONLY using the PDF context.

Question:
{data.question}

Context:
{context}
"""

        response = llm.invoke(prompt)

        answer = response.content
        if isinstance(answer, list):
            answer = answer[0]["text"]

        return {
            "question": data.question,
            "answer": str(answer)
        }

    except Exception as e:
        return {"error": str(e)}