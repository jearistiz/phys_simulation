"""This file manages all requests that are made to our app
"""
from simulation_API import app, templates 
from fastapi import Request, status, BackgroundTasks, HTTPException

from .schemas import SimSystem, SimRequest, SimResultsPaths
from .tasks import _run_simulation


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
        [sys.value, " ".join(sys.value.split("-"))] for sys in SimSystem
    ]

    # Render template
    return templates.TemplateResponse(
        "simulate.html", {"request": request, "sys_values": sys_values}
    )


# Depending on the system the user decides to simulate, there are different 
# routes, bc we need different parameters
@app.get("/simulate/{sim_sys}")
async def simulate_sim_sys(request: Request, sim_sys: SimSystem):
    """Returns a form the user will fill up to request simulation of specific
    system."""
    
    return templates.TemplateResponse(
        f"{sim_sys.value}.html", {"request": request}
    )


# Let the user see all the available results including his/her results
@app.get("/results")
async def results(request: Request):
    """Get info of results and display them all rendering results.html"""
    return templates.TemplateResponse("results.html", {"request": request})


@app.post("/simulate/{sim_sys}")
async def simulate_post_form(request: Request, sim_sys: SimSystem):
    # This will get all the simulation info from the frontend and simulate it
    return

@app.post("/api/simulate/{sim_sys}}/")
async def simulate_Harmonic_Oscillator(
    sim_sys: SimSystem, sim_params: SimRequest
) -> SimResultsPaths:
    """Simulate Harmonic Oscillator Using Backend
    
    Run simulation
    The idea is to run the simulation in the background but I haven't
    found a method to return sthg from the background tasks. Otherwise this
    would not be scalable.
    
    The idea is to obtain sim_results from background and return sim_resuts

    Alternative method would be to just display a message to look at results
    after a moment and give timestamp with milliseconds.
    """

    if not sim_sys.value == sim_params.system:
        raise HTTPException(
            status_code=404,
            detail="Path does not coincide with 'system' entry in request"
        )

    # Simulate system and return relevant info
    sim_results = _run_simulation(sim_params)

    return sim_results