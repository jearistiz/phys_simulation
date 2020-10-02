"""This module initializes our application."""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 

# Initialize application
app = FastAPI(
    title="PHYS Simulation",
    description="An API to request (mainly physics) simulations!",
    version="0.0.1"
)

# Tell FastAPI where to find static files
this_dir = os.path.dirname(__file__)
static_dir = os.path.join(this_dir, 'static')
app.mount(
    "/static", StaticFiles(directory=static_dir), name='static'
)

# # Define instance of jinja class so FastAPI can render them
templates_dir = os.path.join(this_dir, 'templates')
templates = Jinja2Templates(directory=templates_dir)

# Import the file that will manage all the requests made to our app
from simulation_API.controller import main, tasks
