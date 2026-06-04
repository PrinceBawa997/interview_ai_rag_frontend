#Templating in FastAPI

from fastapi import FastAPI,Request # request = needed for templates
from fastapi.responses import HTMLResponse #used when u need to return HTML manually
from fastapi.staticfiles import StaticFiles #used for CSS,JS,images
                                            # this allows to browser to access static folder
from fastapi.templating import Jinja2Templates #this connects FastAPI with HTML templates
                                                # uses jinja2 engine
app = FastAPI()
templates=Jinja2Templates(directory="templates") #it explain where the html file located
@app.get("/",response_class=HTMLResponse) #when someone opens the homepage/, run the fuction below
async def home(request: Request):
    return templates.TemplateResponse("index.html",{
         "request":request,
       "name":"prince"})


templates1=Jinja2Templates(directory="templates1")
@app.get("/",response_class=HTMLResponse)
async def home(request: Request):
    return templates1.TemplateResponse("index.html",{
        "request":request,
        "name":"prince"
    })
