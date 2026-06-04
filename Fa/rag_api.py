import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from pydantic import BaseModel



load_dotenv()
app = FastAPI()
vectorstore=None

@app.post("/pdf")
async def read_pdf(file:UploadFile = File(...)):
    global vectorstore
    with open(file.filename, "wb") as f:
        f.write(await file.read())
        loader=PyPDFLoader(file.filename)
        document=loader.load()

        text=""
        for doc in document:
            text+=doc.page_content



    #chunking
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
    vectorstore=FAISS.from_texts(chunks,embedding)
    return {"message": "file uploaded"}
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.3
    )
class RequestQuestion(BaseModel):
        question: str
@app.post("/question")
async def get_question(data:RequestQuestion):
        global vectorstore
        if vectorstore is None:
            return {"error": "Upload PDF first"}
        docs=vectorstore.similarity_search(data.question,k=5)
        context="\n".join([doc.page_content for doc in docs])
        prompt=f"""
        you are smart AI.
        you read pdf carefully and give clear and eassly understandable answer.
        question: {data.question}
        context: {context}"""
        response=llm.invoke(prompt)
        return{
            "question":data.question,
            "answer":response.content
        }