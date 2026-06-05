import os
import traceback
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

app = FastAPI()

# =========================
# GEMINI LLM
# =========================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# =========================
# EMBEDDINGS (GEMINI)
# =========================
embedding = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# =========================
# GLOBAL STATE
# =========================
vectorstore = None
current_topic = ""

# =========================
# MODELS
# =========================
class RequestTopic(BaseModel):
    topic: str

class RequestAnswer(BaseModel):
    Answer: str

class Question(BaseModel):
    question: str

# =========================
# INTERVIEW TOPIC
# =========================
@app.post("/topic")
async def topic(data: RequestTopic):
    global current_topic
    current_topic = data.topic

    prompt = f"""
Ask interview questions.

Topic: {data.topic}
Generate ONE question only.
"""

    response = llm.invoke(prompt)

    return {"question": response.content}

# =========================
# ANSWER CHECK
# =========================
@app.post("/answer")
async def answer(data: RequestAnswer):

    prompt = f"""
Evaluate answer.

Answer: {data.Answer}

Give:
Score out of 10
Feedback
Correct Answer
Next Question
"""

    response = llm.invoke(prompt)

    return {"result": response.content}

# =========================
# PDF UPLOAD (FIXED FOR RAILWAY)
# =========================
@app.post("/pdf")
async def read_pdf(file: UploadFile = File(...)):

    global vectorstore

    try:
        # 🔥 MUST USE /tmp ON RAILWAY
        file_path = f"/tmp/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        text = " ".join([doc.page_content for doc in documents])

        if not text.strip():
            return {"error": "PDF is empty"}

        words = text.split()

        chunk_size = 300
        overlap = 50
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))

        vectorstore = FAISS.from_texts(chunks, embedding)

        os.remove(file_path)

        return {"message": "PDF uploaded successfully", "chunks": len(chunks)}

    except Exception as e:
        print(traceback.format_exc())
        return {"error": str(e)}

# =========================
# ASK PDF
# =========================
@app.post("/ask")
async def ask(data: Question):

    global vectorstore

    try:
        if vectorstore is None:
            return {"error": "Please upload PDF first"}

        docs = vectorstore.similarity_search(data.question, k=4)

        context = "\n".join([d.page_content for d in docs])

        prompt = f"""
Answer ONLY using context.

Question: {data.question}

Context:
{context}
"""

        response = llm.invoke(prompt)

        return {
            "question": data.question,
            "answer": response.content
        }

    except Exception as e:
        print(traceback.format_exc())
        return {"error": str(e)}