#problem1= searching into text (.txt) document
import langchain_huggingface
from langchain_classic import vectorstores
# from langchain_classic import vectorstores

#
# file=open("/home/prince/Downloads/python_complete_long_notes.txt","r")
# content=file.read()
#
# words=content.split()
# chunks=[]
# chunk_size=50
# chunk_overlap=5
#
# for i in range(0,len(words),chunk_size-chunk_overlap):
#     chunk=words[i:i+chunk_size]
#     chunks.append(" ".join(chunk))
# from langchain_huggingface import HuggingFaceEmbeddings
#
# Embedding=HuggingFaceEmbeddings(
#     model_name="all-MiniLM-L6-v2"
# )
#
# from langchain_community.vectorstores import FAISS
#
# vectorstores=FAISS.from_texts(chunks,Embedding)
#
# query="application of python"
#
# result=vectorstores.similarity_search(query,k=3)
#
# for r in result:
#     print(r.page_content)




# problem 2= searching into pdf
#load pdf
from langchain_community.document_loaders import PyPDFLoader
from sympy.vector import vector

loader=PyPDFLoader("/home/prince/Downloads/PYTHON.pdf")
document=loader.load()

text=""
for doc in document:
    text+=doc.page_content   # also can use "text=text+doc.page_content"

#create chunks

words=text.split()
chunks=[]
chunk_size=100
chunk_overlap=10
for i in range(0,len(words),chunk_size-chunk_overlap):
    chunk=words[i:i+chunk_size]
    chunks.append(" ".join(chunk))

#embedding

from langchain_huggingface import HuggingFaceEmbeddings
embedding=HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

#vector stores(used to store vector and simillarity search)
from langchain_community.vectorstores import FAISS
vectorstores=FAISS.from_texts(chunks,embedding)

#search
query="explain python"
result=vectorstores.similarity_search(query,k=3)
for r in result:
    print(r.page_content)




