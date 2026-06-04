import os
from dotenv import load_dotenv
from langchain_community import vectorstores
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

#file handling

loader = PyPDFLoader("")
document=loader.load()

text=" "
for doc in document:
    text+=doc.page_content

#splittingk
words=text.split()
chunks=[]
chunk_size=100
chunk_overlap=10

for i in range(0,len(words),chunk_size-chunk_overlap):
    chunk=words[i:i+chunk_size]
    chunks.append(" ".join(chunk))

#embeding

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
while True:
    question=input("ask question:")
    if question.lower()=="exit":
        print("stop work")
        break
#simillarity search
    docs=vectorstore.similarity_search(question,k=3)

    context="\n".join([doc.page_content for doc in docs])

#prompt
    prompt=f"""
    you are a smart AI . you gives clear and smart answer of question.
    context:{context}
    question:{question}
     """
    response=llm.invoke(prompt)
    print(response.content)
    print()


