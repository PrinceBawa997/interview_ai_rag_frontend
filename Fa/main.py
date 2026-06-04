from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root():
    return {"message":"prince"}


@app.get("/products/{id}")
def get_product(id: int):
    products=["apple", "banana", "cherry","mango","pineapple","orange"]
    return products[id]

