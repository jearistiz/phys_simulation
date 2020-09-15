"""This file manages all requests that are made to our app
"""
from simulation_API import app, templates 
from fastapi import Request

from .schemas import Sim_system


# This decorator tells us the route and method
# in this case route='domain.com/' and method='get'
@app.get("/")
# La definición async es la que hace a FastAPI realmetn
async def index(request: Request):
    session = {"user_id": 1}
    return templates.TemplateResponse(
        "index.html", {"request": request, "session": session}
    )


# Let the user input the parameters of the simulation
@app.get("/simulate")
async def simulate(request: Request):
    """Renders a template that asks for type of simulation"""
    # Available simulations
    sys_values = [
        [sys.value, " ".join(sys.value.split("-"))] for sys in Sim_system
    ]

    # Render template
    return templates.TemplateResponse(
        "simulate.html", {"request": request, "sys_values": sys_values}
    )


# Depending on the system the user decides to simulate, there are different 
# routes, bc we need different parameters
@app.get("/simulate/{sim_sys}")
async def simulate_sim_sys(request: Request, sim_sys: Sim_system):
    """Returns a form the user will fill up to request simulation of specific
    system."""
    
    return templates.TemplateResponse(
        f"{sim_sys.value}.html", {"request": request}
    )


# Let the user see all the available results including his/her results
@app.get("/results")
async def results(request: Request):
    # Get info of results and display them all rendering results.html
    return templates.TemplateResponse("results.html", {"request": request})


@app.post("/simulate/{sim_sys}")
async def simulate_post(request: Request, ):
    return