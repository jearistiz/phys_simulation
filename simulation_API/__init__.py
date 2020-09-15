"""This file initializes our application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 

# Initialize application
app = FastAPI()

# Tell FastAPI where to find static files
app.mount("/static", StaticFiles(directory='./simulation_API/static'), name='static')

# Define instance of jinja class so FastAPI can render them
templates = Jinja2Templates(directory="./simulation_API/templates")

# Import the file that will manage all the requests made to our app
from simulation_API.views import main
