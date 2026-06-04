from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static",StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")