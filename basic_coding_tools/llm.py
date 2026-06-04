#LLM = large language model
#      used=read text,understand query , give answer, chat like human

import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
#
#
# load_dotenv()
#
# llm=ChatGoogleGenerativeAI(
#     model="gemini-3-flash-preview",
#     temperature=0
# )
# while True:
#     question=input("your question:")
#
#     if question.lower()=="exit":
#         print("stop working")
#         break
#
#     prompt=f"""
#     you are a smart AI who gives best answer of any question.
#     give answer clearly and shortly.
#     user question:
#     {question}
#     """
#     response=llm.invoke(prompt)
#     print(response.content)
#     print()




import os
from fastapi import FastAPI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.store.base import embed
from openai.types import vector_store_list_params
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

#file handling(load file)
loader=PyPDFLoader("/home/prince/Downloads/PYTHON.pdf")
document=loader.load()

text=""
for doc in document:
    text+=doc.page_content

#chunking()
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

#llm
llm=ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.3
)

class RequestQuestion(BaseModel):
    question: str

#api

@app.post("/ask")
def ask_question(data:RequestQuestion):


    docs=vectorstore.similarity_search(data.question,k=3)
    context="\n".join([doc.page_content for doc in docs])

    prompt = f"""
    You are a helpful AI assistant.

    Use the provided context to answer the question.

    If the answer is not found in the context, say:
    "I could not find the answer in the document."
    question: {data.question}
    context: {context}"""

    response=llm.invoke(prompt)

    return{
        "question":data.question,
        "Answer":response.content
    }

