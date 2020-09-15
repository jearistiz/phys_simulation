from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 

# Initialize application
app = FastAPI()

# Tell FastAPI where to find static files
app.mount("/static", directory='./simulation-API/static', name='static')

# Te
templates = Jinja2Templates(directory="./simulation-API/templates")