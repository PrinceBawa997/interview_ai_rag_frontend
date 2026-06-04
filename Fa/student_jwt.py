

from fastapi import FastAPI, HTTPException,Depends

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["students_jwt"]
collection = db["students"]

SECRET_KEY = "MYSECRETKEY"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"
def create_access_token(token:dict):
    to_encode = token.copy()
    expire_time = datetime.now()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire_time})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)

@app.post("/new_student")
def register(student_name:str,password:str):
    if collection.find_one({"username":student_name}):
        raise HTTPException(status_code=400,detail="student already exists")
    hashed_password=hash_password(password)

    collection.insert_one({"username":student_name,"password":hashed_password})
    return{"massage":"student register successfully"}

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/login")
def login(student_name:str,password:str):
    student = collection.find_one({"username":student_name})
    if not student:
        raise(HTTPException(status_code=400,detail="Incorrect Username or Password"))
    if not verify_password(password,student["password"]):
        raise HTTPException(status_code=400,detail="Incorrect Username or Password")

    access_token = create_access_token({"username":student_name})
    return {"access_token":access_token,"token_type":"bearer"}

security=HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token=credentials.credentials

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("username")
        return username
    except JWTError:
        raise HTTPException(status_code=400,detail="Incorrect Username or Password")

@app.post("/protected")
def protected(username:str=Depends(verify_token)):
    return{"message":f"Welcome {username} ,you are authorized"}

