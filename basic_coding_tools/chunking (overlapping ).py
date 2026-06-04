from langchain_community.document_loaders import PyPDFLoader
loader=PyPDFLoader("/home/prince/Downloads/PYTHON.pdf")
document=loader.load()

text=""
for doc in document:
    text+=doc.page_content

words=text.split()
chunks=[]
chunk_size=100
chunk_overlap=10
for i in range(0,len(words),chunk_size-chunk_overlap):
    chunk=words[i:i+chunk_size]
    chunks.append(" ".join(chunk))
print(chunks)

