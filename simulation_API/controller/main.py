"""This file manages all requests that are made to our app
"""
from os.path import isfile
from uuid import uuid4

from simulation_API import app, templates
from fastapi import Request, status, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

# Schemas
from .schemas import *
# Simulation handler
from .tasks import (_run_simulation, _create_pickle_path,
                    _create_sim_status_path, _create_pickle_path_disk,
                    _create_plot_path_disk, na_message)
# Database-related
from simulation_API.model.db import crud, models
from simulation_API.model.db.db_manager import SessionLocal, engine

# Creates all tables (defined in models) in database (simulations.db)
models.Base.metadata.create_all(bind=engine)
# From FastAPI docs https://fastapi.tiangolo.com/tutorial/sql-databases/#alembic-note:
"""Alembic Note
Normally you would probably initialize your database (create tables, etc)
with Alembic.

And you would also use Alembic for "migrations" (that's its main job).

A "migration" is the set of steps needed whenever you change the structure of
your SQLAlchemy models, add a new attribute, etc. to replicate those changes in
the database, add a new column, a new table, etc.
"""


# Dependency. This will instantiate and finally close SessionLocal in every
# route we need to interact with the database.
# Read more: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
def get_db():
    """Starts and ends session in each route that needs database access"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.post("/api/simulate/{sim_system}")
async def api_simulate_sim_system(sim_system: SimSystem,
                                  sim_params: SimRequest,
                                  background_tasks: BackgroundTasks,
                                  db: Session = Depends(get_db)) -> SimIdResponse:
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

    # Create user in database (meanwhile)
    # In production user can NOT be created here, login will be required
    # TODO TODO TODO TODO
    user = UserDBSchCreate(username=sim_params.username)
    user = crud._create_user(db, user)
    # Get user_id from user and store it in sim params !
    sim_params.user_id = user.user_id

    # Create an id for the simulation store it in hex notation
    sim_params.sim_id = uuid4().hex

    # Check that the client is accessing the right path for the right simulation
    # sim_system.value NEEDS to match the request given in JSON as
    # sim_params.system

    if not sim_system.value == sim_params.system.value:
        raise HTTPException(
            status_code=404,
            detail="Path does not coincide with 'system' key value in JSON file"
        )

    # Close ccurrent db connection, so that _run_simulation can update table
    db.close()

    # Simulate system in BACKGROUND
    # TODO TODO TODO Por dentro _run_simulation puede abrir un socket para
    # TODO TODO TODO indicar que la simulación ya se completó
    background_tasks.add_task(_run_simulation, sim_params)

    # Declare some variables needed as params to SimIdResponse
    sim_status_path = _create_sim_status_path(sim_params.sim_id)
    sim_pickle_path = _create_pickle_path(sim_params.sim_id)

    message1 = "(When –and if– available) request via GET your simulation's" \
               "status in route 'sim_status_path' or download your results" \
               "(pickle fomat) via GET in route 'sim_pickle_path'"
    message2 = na_message
    message = message1 if sim_params.system == SimSystem.Harmonic_Oscillator else message2

    sim_id_response = SimIdResponse(
        sim_id=sim_params.sim_id,
        user_id=sim_params.user_id,
        username=sim_params.username,
        sim_system=sim_params.system,
        sim_status_path=sim_status_path,
        sim_pickle_path=sim_pickle_path,
        message=message
    )

    return sim_id_response


@app.get("/api/results/{sim_id}")
async def api_results_sim_id(sim_id: str,
                             db: Session = Depends(get_db)) -> SimStatus:
    """Get status of previously requested simulation"""

    # Simulation status
    sim_status = crud._get_simulation(db, sim_id)
    # Plot uery params possible values
    plot_query_values = crud._get_plot_query_values(db, sim_id)
    # Parameters
    params = crud._get_parameters(db, sim_id, ParamType.param)
    # Initial conditions
    ini_cndtn = crud._get_parameters(db, sim_id, ParamType.ini_cndtn)

    return SimStatus(
        ini_cndtn = ini_cndtn,
        params=params,
        plot_query_values=plot_query_values,
        **sim_status.__dict__
    )


@app.get("/api/results/{sim_id}/pickle")
async def api_results_sim_id(sim_id: str):
    """Download pickle of previously requested simulation. Here we use
    FileResponse from starlette.responses
    """
    pickle_path_disk = _create_pickle_path_disk(sim_id)

    if not isfile(pickle_path_disk):
        message = "The file you requested is not in our database. " \
                  "If your smulation id (sim_id) is correct, there might be " \
                  "an internal server error and the file you requested is " \
                  "not available."
        raise HTTPException(404, detail=message)

    return FileResponse(pickle_path_disk, media_type="binary",
                        filename=sim_id + ".pickle")


# `plot_id` is a query parameter and its value must match one of the plot_ids
# given in simulation status via GET in route "/api/results/{sim_id}"
@app.get("/api/results/{sim_id}/plot")
async def api_results_sim_id(sim_id: str, value: str):
    """Download plot of previously requested simulation. Note one query param
    is required here. Here we use FileResponse from starlette.responses
    """

    plot_path_disk = _create_plot_path_disk(sim_id, value)

    if not isfile(plot_path_disk):
        message = "The plot you requested is not in our database. " \
                  "If your smulation id (sim_id) and the query param " \
                  "'value' are correct, there might be an internal server "\
                  "error and the plot you requested is not available."
        raise HTTPException(404, detail=message)

    return FileResponse(plot_path_disk, media_type="png",
                        filename=sim_id + ".png")
