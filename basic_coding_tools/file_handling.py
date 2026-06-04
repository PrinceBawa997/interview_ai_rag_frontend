import langchain_community

# file=open("/home/prince/Downloads/python_complete_long_notes.txt","r")
# text=file.read()
#
# print(text)
#
# file.close()


# for pdf


#dynamic file handling
from fastapi import FastAPI, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader

app = FastAPI()

@app.post("/read")
async def read_pdf(file: UploadFile = File(...)):

    with open(file.filename, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(file.filename)
    documents = loader.load()

    text = ""

    for doc in documents:
        text += doc.page_content

    return {"message": "file uploaded",
            "text":text}