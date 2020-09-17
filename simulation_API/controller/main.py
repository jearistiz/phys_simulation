"""This file manages all requests that are made to our app
"""
from simulation_API import app, templates 
from fastapi import Request, status, BackgroundTasks, HTTPException
from starlette.responses import FileResponse

from .schemas import SimSystem, SimRequest, SimIdResponse, SimStatus
from .tasks import _run_simulation
from uuid import uuid4


# This decorator tells us the route and method
# in this case route='domain.com/' and method='get'
@app.get("/")
# La definición async es la que hace a FastAPI realmetn
async def index(request: Request):
    session = {"user_id": 1}
    return templates.TemplateResponse(
        "index.html", {"request": request, "session": session}
    )


# Let the user see all the available results including his/her results
@app.get("/results")
async def results(request: Request):
    """Get info of results and display them all rendering results.html"""
    return templates.TemplateResponse("results.html", {"request": request})


@app.get("/results/{sim_system}/{sim_id}")
async def results_sim_system_sim_id(sim_system: SimSystem):
    """Show results of simulation in frontend"""

    # TODO TODO TODO
    # TODO TODO TODO
    # TODO TODO TODO

    return


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
@app.get("/simulate/{sim_system}")
async def simulate_sim_system(request: Request, sim_system: SimSystem):
    """Returns a form the user will fill up to request simulation of specific
    system."""
    
    return templates.TemplateResponse(
        f"{sim_system.value}.html", {"request": request}
    )


@app.post("/simulate/{sim_system}")
async def simulate_post_form(request: Request, sim_system: SimSystem):
    # This will get all the simulation info from the frontend and simulate it
    
    # TODO TODO TODO
    # TODO TODO TODO
    # TODO TODO TODO
    
    return {"message": "Working on it"}


@app.post("/api/simulate/{sim_system}")
async def api_simulate_sim_system(sim_system: SimSystem,
                                  sim_params: SimRequest,
                                  background_tasks: BackgroundTasks) -> SimIdResponse:
    """Simulate Harmonic Oscillator Using BackgroundTasks
    
    When cient requests a simulation via '/api/simulate/{sim_system}', he/she
    obtains relevant information on how to get the results of the simulation.

    Parameters
    ----------
    sim_system : SimSystem
        String declaring the system to be simulated (in path).
    sim_params : SimRequest
        Simulation request. JSONSchema declared in schemas.py
    background_tasks : BackgroundTasks
        Background task FastAPI manager (Class). 
    
    Returns
    -------
    sim_id_response : SimIdResponse
        JSON containing relevant info on the simulation and how to get the
        results.
    """
    
    # Create an id for the simulation store it in hex notation
    sim_params.sim_id = uuid4().hex

    # Get user_id somehow from logging (production)
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO 
    # Right now just using user_id = 1 for all querys
    sim_params.user_id = 1

    # Check that the client is accessing the right path for the right simulation
    # sim_system.value NEEDS to match the request given in JSON as
    # sim_params.system
    if not sim_system.value == sim_params.system:
        raise HTTPException(
            status_code=404,
            detail="Path does not coincide with 'system' key value in JSON file"
        )

    # Simulate system in BACKGROUND
    background_tasks.add_task(_run_simulation, sim_params)

    # Declare some variables needed as params to SimIdResponse
    sim_status_path = f'/api/results/{sim_params.sim_id}'
    sim_pickle_path = f'/api/results/{sim_params.sim_id}/pickle'

    message = f"(When –and if– available) request via GET your simulation's status in route 'sim_status_path' or download your results (pickle fomat) via GET in route 'sim_pickle_path'" if sim_params.system == SimSystem.ho else "This simulation is not available at the moment"

    sim_id_response = SimIdResponse(
        sim_id=sim_params.sim_id,
        sim_system=sim_params.system,
        sim_status_path=sim_status_path,
        sim_pickle_path=sim_pickle_path,
        message=message
    )

    return sim_id_response


@app.get("/api/results/{sim_id}")
async def api_results_sim_id(sim_id: str):
    """Get status of previously requested simulation"""
    
    # TODO TODO TODO
    # TODO TODO TODO
    # TODO TODO TODO
    
    return {"message": "Working on it"}

@app.get("/api/results/{sim_id}/pickle")
async def api_results_sim_id(sim_id: str):
    """Download pickle of previously requested simulation. Here we use
    FileResponse from starlette.responses
    """
    
    # TODO TODO TODO see https://www.starlette.io/responses/#fileresponse
    # TODO TODO TODO see https://www.starlette.io/responses/#fileresponse
    # TODO TODO TODO see https://www.starlette.io/responses/#fileresponse
    
    return {"message": "Working on it"}

# `plot_id` is a query parameter and its value must match one of the plot_ids
# given in simulation status via GET in route "/api/results/{sim_id}"
@app.get("/api/results/{sim_id}/plot")
async def api_results_sim_id(sim_id: str, plot_id : str):
    """Download plot of previously requested simulation. Note one query param
    is required here. Here we use FileResponse from starlette.responses
    """
    
    # TODO TODO TODO see https://www.starlette.io/responses/#fileresponse
    # TODO TODO TODO see https://www.starlette.io/responses/#fileresponse
    # TODO TODO TODO see https://www.starlette.io/responses/#fileresponse
    
    return {"message": "Working on it"}