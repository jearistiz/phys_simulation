"""This file manages all requests that are made to our app
TODO|FIXME|BUG|HACK|NOTE|
"""
from os.path import isfile
from uuid import uuid4

import requests
from fastapi import Request, BackgroundTasks, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, RedirectResponse


# App instance and templates
from simulation_API import app, templates
# Schemas
from .schemas import *
# Simulation handler
from .tasks import (_run_simulation, _create_pickle_path,
                    _create_sim_status_path, _create_pickle_path_disk,
                    _create_plot_path_disk, _sim_form_to_sim_request)
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
async def simulate_sim_system(request: Request, 
                              sim_system: SimSystem):
    """Returns a form the user will fill up to request simulation of specific
    system."""

    sim_form = SimFormDict[sim_system.value]()

    # FIXME FIXME FIXME REMOVE NEXT LINE
    # FIXME FIXME FIXME REMOVE NEXT LINE
    # FIXME FIXME FIXME REMOVE NEXT LINE
    print(sim_form)

    return templates.TemplateResponse(
        f"{sim_system.value.lower()}.html",
        {
            "sim_system": str(sim_system.value),
            "request": request,
            "integration_methods": integration_methods,
            **sim_form.dict(),
        }
    )


@app.post("/simulate/{sim_system}")
async def simulate_post_form(request: Request, sim_sys: SimSystem = Form(...), 
                             username: str = Form(...), t0: float = Form(...),
                             tf: float = Form(...), dt: float = Form(...),
                             method: IntegrationMethods = Form(...)):
    """This route will receive the form requesting a simulation (and filled in
    frontend via GET in route "/simulate/{sim_system}"). The simulation is
    internally requested via the API in route "/api/simulate/{sim_system} via
    POST. Finally the client is redirected to the "Simulation Status" frontend
    page, where further information about the simulation is displayed.
    """
    # This will get all the simulation info from the frontend and simulate it
    
    # Here we get form directly from request.
    # NOTE The other method is using FastAPI's Form function, but here it is
    # easier to access the form directly from request (as below).
    # NOTE This method does NOT provide pydantic type checking. However, type
    # checking is more or less provided in the frontend by the form itself.
    form = await request.form()
    form = form.__dict__['_dict']

    # TODO TODO TODO request simulation from the backend via route 
    # "/api/simulate/{sim_system}"
    # Change format from form data to SimRequest schema.
    sim_request = _sim_form_to_sim_request(form)

    request_simulation_url = app.url_path_for(
        "api_request_sim",
        sim_system=sim_request.system.value
    )

    # FIXME La idea es solicitar la simulación con la misma api
    # (/api/simulate/{sim_system}) y luego renderizar una página con la info
    # del estatus de la simulación que retorna esta ruta
    # FIXME req = RedirectResponse(request_simulation_url)
    # FIXME req = requests.post("http://0.0.0.0:5700" + request_simulation_url, data=sim_request.json() )
    # print("\n\n\n", req, "\n\n\n")
    
    # TODO TODO TODO Chage this return. Instead, render a template with
    # sim_request data.
    return sim_request


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


@app.post("/api/simulate/{sim_system}", name="api_request_sim")
async def api_simulate_sim_system(sim_system: SimSystem,
                                  sim_params: SimRequest,
                                  background_tasks: BackgroundTasks,
                                  db: Session = Depends(get_db)) -> SimIdResponse:
    """Simulate Harmonic Oscillator Using BackgroundTasks

    When client requests a simulation via '/api/simulate/{sim_system}', he/she
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
    message = message1 if sim_params.system == SimSystem.HO else message2

    sim_id_response = SimIdResponse(
        sim_id=sim_params.sim_id,
        user_id=sim_params.user_id,
        username=sim_params.username,
        sim_sys=sim_params.system,
        sim_status_path=sim_status_path,
        sim_pickle_path=sim_pickle_path,
        message=message
    )

    return sim_id_response


@app.get("/api/results/status/{sim_id}")
async def api_results_sim_id(sim_id: str,
                             db: Session = Depends(get_db)) -> SimStatus:
    """Get status of previously requested simulation"""

    # Simulation status
    sim_status = crud._get_simulation(db, sim_id)
    # Plot query params possible values
    plot_query_values = [
        "?value=" + value for value in crud._get_plot_query_values(db, sim_id)
    ]
    # Parameters
    params = crud._get_parameters(db, sim_id, ParamType.param)
    # Initial conditions
    ini_cndtn = crud._get_parameters(db, sim_id, ParamType.ini_cndtn)

    sim_status_NA = {
        "sim_id": "NA",
        "user_id": 0,
        "date": str(datetime.utcnow()),
        "system": "Harmonic-Oscillator",
        "success": False,
        "message": sim_id_not_found_message
    }

    sim_status = sim_status.__dict__ if sim_status else sim_status_NA

    sim_status_complete = {
        "ini_cndtn": ini_cndtn,
        "params": params,
        "plot_query_values": plot_query_values,
        **sim_status,
    }

    return SimStatus(**sim_status_complete)


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
    
    # Media type application/octet-stream is any type of binary data
    # The technical name of media types is "MIME types"
    return FileResponse(pickle_path_disk, media_type="application/octet-stream",
                        filename=sim_id + ".pickle")


# `value` is a query parameter and its value must match one of the plot_ids
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

    return FileResponse(plot_path_disk, media_type="image/png",
                        filename=sim_id + ".png")
