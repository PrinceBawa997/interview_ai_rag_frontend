from fastapi import FastAPI, HTTPException,Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime, timedelta



app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["jwt"]
collection = db["users"]
class User(BaseModel):
    username: str
    password: str

SECRET_KEY ="PRIVATE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(token: dict):
    to_encode = token.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

@app.post("/register")
def register_user(username:str,password:str,):
    if collection.find_one({"username":username}):
        raise HTTPException(status_code=400,detail="Incorrect Password")
    hashed_password = hash_password(password)
    collection.insert_one({"username":username,"password":hashed_password})
    return{"message":"user registered"}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/login")
def login_user(username:str,password:str):

    user_login = collection.find_one({"username": username})
    if not user_login:
        raise HTTPException(status_code=400,detail="Incorrect Username or Password")
    if not verify_password(password, user_login["password"]):
        raise HTTPException(status_code=400,detail="Incorrect Username or Password")

    access_token = create_access_token({"sub": username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



security=HTTPBearer()
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token=credentials.credentials
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except JWTError:
        raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
@app.get("/protected")
def protected_route(username:str=Depends(verify_token)):
    return{"message":f"welcome{username},you are authiorized"}











