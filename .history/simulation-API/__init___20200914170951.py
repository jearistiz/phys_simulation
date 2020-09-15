from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 

app = FastAPI()

app.mount("/static", directory='./simulation-API/static', name='static')
templates = Jinja2Templates(directory="./simulation-API/templates")