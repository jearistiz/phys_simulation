"""This file manages all requests that are made to our app
TODO|FIXME|BUG|HACK|NOTE|
"""
from os.path import isfile

from fastapi import Request, BackgroundTasks, HTTPException, Depends, Form
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_404_NOT_FOUND
from sqlalchemy.orm import Session



# App instance and templates
from simulation_API import app, templates
# Schemas
from .schemas import *
# Simulation handler
from .tasks import (_create_pickle_path_disk, _create_plot_path_disk, 
                    _sim_form_to_sim_request, _api_simulation_request)
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
    """Index"""

    route_simulate = app.url_path_for("frontend_simulate")
    route_results = app.url_path_for("frontend_results")

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "route_simulate": route_simulate,
            "route_results": route_results
        }
    )


# Let the user input the parameters of the simulation
@app.get("/simulate", name="frontend_simulate")
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
@app.get("/simulate/{sim_system}", name="frontend_request_simulation")
async def simulate_sim_system(request: Request, 
                              sim_system: SimSystem,
                              error_message: Optional[str] = ''):
    """Returns a form the user will fill up to request simulation of specific
    system."""

    # Get Simulation form schema depending on system and instantiate it. This
    # schema contains the default values for initial conditions and parameters
    SysSimForm = SimFormDict[sim_system.value]
    sim_form = SysSimForm()

    return templates.TemplateResponse(
        f"request-simulation.html",
        {
            "sim_system": str(sim_system.value),
            "request": request,
            "integration_methods": integration_methods,
            "error_message": error_message,
            **sim_form.dict(),
        }
    )


@app.post("/simulate/{sim_system}")
async def simulate_post_form(request: Request, background_tasks: BackgroundTasks,
                             db: Session = Depends(get_db),
                             sim_sys: SimSystem = Form(...), 
                             username: str = Form(...), t0: float = Form(...),
                             tf: float = Form(...), dt: float = Form(...),
                             method: IntegrationMethods = Form(...)):
    """This route will receive the form requesting a simulation (and filled in
    frontend via GET in route "/simulate/{sim_system}"). The simulation is
    internally requested via the API in route "/api/simulate/{sim_system} via
    POST. Finally the client is redirected to the "Simulation Status" frontend
    page, where further information about the simulation is displayed.
    """
    # Here we get form directly from request.
    # NOTE The other method is using FastAPI's Form function, but here it is
    # easier to access the form directly from request (as below).
    # NOTE This method does NOT provide pydantic type checking. However, type
    # checking is more or less provided in the frontend by the form itself.
    form = await request.form()
    form = form.__dict__['_dict']
    
    # Change all parameters and initial conditions to float
    # keys_ini_condition = [key for key in form if key[:3]=="ini"]
    # ini_cndtns = {
    #     f"ini{i}": float(form[f"ini{i}"]) 
    #         for i in range(len(keys_ini_condition))
    # }
    # keys_params = [key for key in form if key[:5]=="param"]
    # params = {
    #     f"ini{i}": float(form[f"ini{i}"]) 
    #         for i in range(len(keys_params))
    # }
    
    # form = {**form, **params, **ini_cndtns}


    # Check t_0 < t_f
    # TODO TODO TODO FIXME Render form again with error message if t0 > tf
    t_0 = form["t0"]
    t_f = form["tf"]
    if not t_0 < t_f:
        url_frontend_sim_request = app.url_path_for(
            "frontend_request_simulation",
            sim_system=form["sim_sys"],
        )
        req = RedirectResponse(
            url_frontend_sim_request + "?message=t0%20<%20tf"
        )
        return req

    # Change format from form data to SimRequest schema.
    sim_request = _sim_form_to_sim_request(form)
    
    # BUG? Is the simulation request as done in the next lines of code OK?
    # 
    # FIXME
    #  
    # In the first place I was thinking of asking the API to somehow internally
    # go to route "/api/simulate/{sim_system}" BUT I could not do that.
    # I tried using the methods shown below: 
    # 
    # NOTE Method 1) using request.post()
    # request_simulation_url = app.url_path_for(
    #     "api_request_sim",
    #     sim_system=sim_request.system.value
    # )
    # req = requests.post("http://0.0.0.0:5700" + request_simulation_url, data=sim_request.json())
    #
    # NOTE Method 2) using RedirectResponse
    # req = RedirectResponse(request_simulation_url)
    #
    # Neither of the methods worked so I solved it by just doing the same as in
    # route "/api/simulate/{sim_system}" (calling _api_simulation_request as
    # done below)
    
    # Request simulation from backend and get sim_id_response
    sim_id_response = _api_simulation_request(sim_sys, sim_request,
                                              background_tasks, db)
    
    # Redirect client to success page
    # POST/REDIRECT/GET Strategy with code 303
    # https://en.wikipedia.org/wiki/Post/Redirect/Get 
    simulation_id_url = app.url_path_for(
        "frontend_simulation_id",
        sim_id=sim_id_response.sim_id
    )
    req = RedirectResponse(simulation_id_url,
                           status_code=HTTP_303_SEE_OTHER)
    
    dict_info = {"sim_request": sim_request,"sim_id_response": sim_id_response}

    return req


@app.get("/simulate/id/{sim_id}", name="frontend_simulation_id")
async def simulate_id_sim_id(request: Request, sim_id: str):
    """Show simulation id after askinf for simulation in frontend via POST in
    route '/simulate/{sim_system}'
    """
    sim_status_url = app.url_path_for(
        "fronted_simulation_status",
        sim_id=sim_id
    )

    # This same template is used to show simulation id info or simulation
    # status info, here we need simulation id info, so we set status=False.
    return templates.TemplateResponse(
        "simulation-id-or-status.html",
        {
            "request": request,
            "status": False,
            "sim_id": sim_id,
            "sim_status_url": sim_status_url,
        }
    )


@app.get("/simulate/status/{sim_id}", name="fronted_simulation_status")
async def simulate_status_sim_id(request: Request, sim_id: str,
                                 db: Session = Depends(get_db)):
    sim_info = crud._get_simulation(db, sim_id)
    username = crud._get_username(db, sim_info.user_id)
    params = crud._get_parameters(db, sim_id, ParamType.param.value)
    plot_query_values = crud._get_plot_query_values(db, sim_id)

    plots_url = app.url_path_for(
        "api_download_plots",
        sim_id=sim_id
    )
    path_plots = [plots_url + "?value=" + value for value in plot_query_values]

    ini_cndtn = crud._get_parameters(db, sim_id, ParamType.ini_cndtn.value)

    # This same template is used to show simulation id info or simulation
    # status info, here we need simulation status so we set status=True.
    return templates.TemplateResponse(
        "simulation-id-or-status.html",
        {
            "request": request,
            "username": username[0],
            "status": True,
            "ini_cndtn": ini_cndtn,
            "params": params,
            "path_plots": path_plots,
            **sim_info.__dict__
        }
    )


# Let the user see all the available results including his/her results
@app.get("/results", name="frontend_results")
async def results(request: Request, db: Session = Depends(get_db)):
    """Get info of results and display them all rendering results.html"""
    # Pull all simulations from database
    simulations = crud._get_all_simulations(db)
    simulations = [simulation.__dict__ for simulation in simulations]
    sim_status_url = app.url_path_for("fronted_simulation_status", sim_id="0")
    
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "simulations": simulations,
            "sim_status_url": sim_status_url,
        }
    )


@app.get("/results/{sim_system}/{sim_id}")
async def results_sim_system_sim_id(request: Request, sim_system: SimSystem,
                                    sim_id: str):
    """Show results of simulation in frontend"""

    # TODO TODO TODO
    # TODO Design a more general template that does not depend strongly on the simulation

    plot_paths = app.url_path_for("api_download_plots", sim_id=sim_id)
    route_pickle = app.url_path_for("api_download_pickle", sim_id=sim_id)
    plot_path_coord = plot_paths + "?value=coord"
    plot_path_phase = plot_paths + "?value=phase"
    results_info = {
        "sim_sys": sim_system.value,
        "route_coord_plot": plot_path_coord,
        "route_phase_plot": plot_path_phase,
        "route_pickle": route_pickle
    }

    return templates.TemplateResponse(
        "results-show.html",
        {
            "request": request,
            **results_info
        }
    )


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

    sim_id_response = _api_simulation_request(sim_system, sim_params,
                                              background_tasks, db)

    return sim_id_response


@app.get("/api/simulate/status/{sim_id}", name="api_simulate_status")
async def api_results_sim_id(sim_id: str,
                             db: Session = Depends(get_db)) -> SimStatus:
    """Get status of previously requested simulation"""

    # Simulation status
    sim_status = crud._get_simulation(db, sim_id)
    # Plot query params possible values
    plot_query_values = crud._get_plot_query_values(db, sim_id)

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


@app.get("/api/results/{sim_id}/pickle", name="api_download_pickle")
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
@app.get("/api/results/{sim_id}/plot", name="api_download_plots")
async def api_results_sim_id(sim_id: str, value: str):
    """Download plot of previously requested simulation. Note one query param
    is required here. Here we use FileResponse from starlette.responses
    """

    plot_path_disk = _create_plot_path_disk(sim_id, value)

    if not isfile(plot_path_disk):
        message = "The plot you requested is not in our database. " \
                  "If your smulation id (sim_id) and the query param " \
                  "'value' are correct, there might be an internal server " \
                  "error and the plot you requested is not available."
        raise HTTPException(404, detail=message)

    return FileResponse(plot_path_disk, media_type="image/png",
                        filename=sim_id + "_" + value + ".png")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request,
                                        exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "404.html",
        {
            "request": request,
        }
    )
