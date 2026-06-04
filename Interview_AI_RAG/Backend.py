import os
from fastapi import FastAPI,UploadFile,File
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel


load_dotenv()

app=FastAPI()

#llm

llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# interview AI

class RequestTopic(BaseModel):
    topic: str
class RequestAnswer(BaseModel):
    Answer: str
current_topic=""

@app.post("/topic")
async def topic(data: RequestTopic):
    global current_topic
    current_topic=data.topic
    prompt=f"""
 ask only eassy question. in starting and increase difficulty level.
 topic: {data.topic}
    Generate only ONE interview question.
    Do not provide answer.
    """
    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        question = response.content[0]["text"]
    else:
        question = response.content
    return {"topic": question}

@app.post("/answer")
async def answer(data: RequestAnswer):
    global current_topic
    current_topic=data.Answer
    prompt = f"""
        you are a expert interviewer.

        answer ={data.Answer}
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

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        answer = response.content[0]["text"]
    else:
        answer = response.content

    return {"Answer": answer}


# RAG

#file handling
vectorstore=None
@app.post("/pdf")
async def read_pdf(file:UploadFile=File(...)):
    global vectorstore
    with open(file.filename,'wb') as f:
        f.write(await file.read())
    loader=PyPDFLoader(file.filename)
    document=loader.load()

    text=""
    for doc in document:
        text+=doc.page_content


    #chunking(text splliting)
    words=text.split()
    chunks=[]
    chunk_size=100
    chunk_overlap=10

    for i in range(0,len(words),chunk_size-chunk_overlap):
        chunk=words[i:i+chunk_size]
        chunks.append(" ".join(chunk))

    #embedding

    embedding=HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    #vector db

    if os.path.exists(file.filename):
        os.remove(file.filename)
    vectorstore=FAISS.from_texts(chunks,embedding)

    return{"message":"file uploaded successfully"}

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

        context = "\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
You are a smart AI assistant.

Answer the question using only the PDF context.

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

        return {
            "error": str(e)
        }