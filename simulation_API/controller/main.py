"""This file manages all requests that are made to our app
TODO|FIXME|BUG|HACK|NOTE|
"""
from os.path import isfile
from uuid import UUID

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

"""
From FastAPI docs https://fastapi.tiangolo.com/tutorial/sql-databases/#alembic-note:

Alembic Note
------------
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
    """Index web page
    
    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    Returns
    -------
    TemplateResponse : TemplateResponse
        Renders greeting template and hyperlinks to simulation rquests and
        results.
    """

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
    """Simulate web page.
    
    Here the users can select between the available systems to simulate the one
    they choose.

    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    Returns
    -------
    TemplateResponse : TemplateResponse
        Renders template displaying the available systems to be simulated.
    """
    # Available simulations
    sys_values = [
        [sys.value, sys.value.replace("-", " ")] for sys in SimSystem
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
    """Simulation's form web page.
    
    The users input the desired parameters for the simulation of their
    choosing.

    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.
    
    sim_request : SimSystem
        
        System to be simulated. This has to be one of the available systems
        defined in SimSystem in schemas.py
    
    error_message : str
        
        Internally used by the backend to display error messages in forntend
        form.

    Returns
    -------
    TemplateResponse : TemplateResponse
        Renders template displaying the form.
    """

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
async def simulate_post_form(request: Request, sim_system: SimSystem,
                             background_tasks: BackgroundTasks,
                             db: Session = Depends(get_db),
                             sim_sys: SimSystem = Form(...),
                             username: str = Form(...), t0: float = Form(...),
                             tf: float = Form(...), dt: float = Form(...),
                             method: IntegrationMethods = Form(...)):
    """Receives the simulation request information from the frontend form and
    requests the simulation to the backend.
    
    This route receives the form requesting a simulation (and filled in
    frontend via GET in route "/simulate/{sim_system}"). The simulation is
    internally requested using the function `_api_simulation_request`.
    Finally the client is redirected to the "Simulation ID" frontend web
    page, where further information about the simulation is displayed.

    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    sim_system : SimSystem

        System to be simulated. Must be one of the members of SimSystem.

    background_tasks : BackgroundTasks

        Needed to request simulation to the backend (in background). Handled
        internally by the API.

    db : Session

        Database Session, needed to interact with database. This is handled 
        internally.

    sim_sys : SimSystem

        Form entry: system to be simulated. Must be one of the members of
        SimSystem.

    username : str
        
        Form entry: name of the user requesting the simulation.

    t0 : float
        
        Form entry: initial time of simulation.

    tf : float
        
        Form entry: final time of simulation.

    dt : float
        
        Form entry: timestep of simulation.

    method : IntegrationMethods
        
        Form entry: method of integration. Must be a member of
        IntegrationMethods.

    Returns
    -------
    
    TemplateResponse or RedirectResponse
        
        Redirects the user either to "Simulation ID" frontend web page or –if
        the user made a mistake filling the form– to the form again.
    
    Notes
    -----
    The parameters of the form accessed by FastAPI's Form class are only
    declared as parameters so that pydantic checks the types, but they are not
    used directly to request the simulation. Here, we access the form directly
    by using the request.form() method as can be seen in the first lines. This
    allows us a better control over the data and also to handle different type
    of forms –which depend on the simulation because parameters and initial
    conditions are intrinsically different for different systems.
    """
    # Here we get form directly from request.
    # NOTE The other method is using FastAPI's Form function, but here it is
    # easier to access the form directly from request (as below).
    # NOTE This method does NOT provide pydantic type checking. However, type
    # checking is more or less provided in the frontend by the form itself.
    form = await request.form()
    form = form.__dict__['_dict']

    # Check for some errors
    error_message = ""
    if not t0 < tf:
        error_message = "in Time Stamp, t0 must be less than tf"
    elif not tf - t0 > dt or dt <= 0:
        error_message = "in Time Stamp, dt must be within 0 and tf - t0"
    if error_message:
        SysSimForm = SimFormDict[sim_system.value]
        sim_form = SysSimForm()
        return templates.TemplateResponse(
            "request-simulation.html",
            {
                "sim_system": str(sim_system.value),
                "request": request,
                "integration_methods": integration_methods,
                "error_message": error_message,
                **sim_form.dict(),
            },
            status_code=400
        )

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
    
    # Redirect client to 'success' page
    # POST/REDIRECT/GET Strategy with 303 status code
    # https://en.wikipedia.org/wiki/Post/Redirect/Get 
    simulation_id_url = app.url_path_for(
        "frontend_simulation_id",
        sim_id=sim_id_response.sim_id
    )
    req = RedirectResponse(simulation_id_url,
                           status_code=HTTP_303_SEE_OTHER)

    return req


@app.get("/simulate/id/{sim_id}", name="frontend_simulation_id")
async def simulate_id_sim_id(request: Request, sim_id: str):
    """Shows simulation id after asking for simulation in frontend form.

    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    sim_id : str

        ID of the simulation.

    Returns
    -------
    TemplateResponse : TemplateResponse

        Renders template displaying the simulation ID and a hyperlink to
        further information about the simulation.
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
    """Shows simulation status for a given simulation via its `sim_id`

    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    sim_id : str

        ID of the simulation.

    db : Session

        Database Session, needed to interact with database. This is handled 
        internally.

    Returns
    -------
    TemplateResponse : TemplateResponse

        Renders a template displaying the simulation status and a hyperlinks to
        simulation results in several formats. If simulation id is not
        available, renders a message about the situation.
    """
    try:
        sim_info = crud._get_simulation(db, sim_id)
        username = crud._get_username(db, sim_info.user_id)
    except:
        return templates.TemplateResponse(
            "simulation-id-or-status.html",
            {
                "request": request,
                "sim_id": sim_id,
                "status": True,
                "not_finished": True,
            }
        )

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
    """Shows a list of all the available simulation results.
    
    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    db : Session

        Database Session, needed to interact with database. This is handled 
        internally.

    Returns
    -------
    TemplateResponse : TemplateResponse

        Renders template displaying all the available simulation results.
    """
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
    """Show graphic results of simulation in frontend for given sim_id
    
    Parameters
    ----------
    request : Request

        HTTP request, used internally by FastAPI.

    sim_system : SimSystem

        System to be simulated. Must be one of the members of SimSystem.

    sim_id : str

        ID of the simulation.

    Returns
    -------
    TemplateResponse : TemplateResponse

        Renders a template displaying all the generated plots for a given
        simulation.
    """

    # Pickle download route
    route_pickle = app.url_path_for("api_download_pickle", sim_id=sim_id)

    # Plot download routes
    plot_paths = app.url_path_for("api_download_plots", sim_id=sim_id)
    if sim_system == SimSystem.HO.value:
        coord = PlotQueryValues_HO.coord.value
        phase = PlotQueryValues_HO.phase.value
        plot_routes = {
            coord: plot_paths + "?value=" + coord,
            phase: plot_paths + "?value=" + phase,
        }
    elif sim_system == SimSystem.ChenLee.value:
        threeD = PlotQueryValues_ChenLee.threeD.value
        project = PlotQueryValues_ChenLee.project.value
        plot_routes = {
            threeD: plot_paths + "?value=" + threeD,
            project: plot_paths + "?value=" + project
        }
    else:
        plot_routes = {}
    
    results_info = {
        "sim_sys": sim_system.value,
        "sim_id": sim_id,
        "route_pickle": route_pickle,
    }

    return templates.TemplateResponse(
        "results-show.html",
        {
            "request": request,
            "plot_routes": plot_routes,
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

        System to be simulated. Must be one of the members of SimSystem.

    sim_params : SimRequest

        Simulation request information with schema given by SimRequest and
        decalared in schemas.py.

    background_tasks : BackgroundTasks

        Background task FastAPI manager (Class). This is handled internally.

    db : Session

        Database Session, needed to interact with database. This is handled 
        internally.

    Returns
    -------
    sim_id_response : SimIdResponse

        JSON containing relevant info about the simulation and how to get the
        results.
    """

    sim_id_response = _api_simulation_request(sim_system, sim_params,
                                              background_tasks, db)

    return sim_id_response


@app.get("/api/simulate/status/{sim_id}", name="api_simulate_status")
async def api_results_sim_id(sim_id: str,
                             db: Session = Depends(get_db)) -> SimStatus:
    """Shows status of requested simulation

    Parameters
    ----------
    sim_id : str

        ID of the simulation.

    db : Session

        Database Session, needed to interact with database. This is handled 
        internally.

    Returns
    -------
    SimStatus : SimStatus

        JSON containing status of the simulation and how to get the results.
    """

    # Simulation status
    sim_status = crud._get_simulation(db, sim_id)
    # Plot query params possible values
    plot_query_values = crud._get_plot_query_values(db, sim_id)

    # Parameters
    params = crud._get_parameters(db, sim_id, ParamType.param)
    # Initial conditions
    ini_cndtn = crud._get_parameters(db, sim_id, ParamType.ini_cndtn)

    sim_status_NA = {
        "sim_id": sim_id,
        "user_id": 0,
        "date": str(datetime.utcnow()),
        "system": None,
        "success": None,
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
    """Download pickle of previously requested simulation. 

    Parameters
    ----------
    sim_id : str

        ID of the simulation.

    Returns
    -------
    FileResponse : FileResponse

        FileResponse from starlette.responses containing the simulation results
        in pickle format.
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
async def api_results_sim_id(sim_id: str, value: PlotQueryValues):
    """Download plot of previously requested simulation. Note one query param
    is required here. Here we use FileResponse from starlette.responses
    
    Parameters
    ----------
    sim_id : str

        ID of the simulation.

    value : PlotQueryValues

        Query values. Must be a member of one of the Enum classes given in
        PlotQueryValues.

    Returns
    -------
    FileResponse : FileResponse

        FileResponse from starlette.responses containing the requested plot.
    """

    plot_path_disk = _create_plot_path_disk(sim_id, value.value)

    if not isfile(plot_path_disk):
        message = "The plot you requested is not in our database. " \
                  "If your smulation id (sim_id) and the query param " \
                  "'value' are correct, there might be an internal server " \
                  "error and the plot you requested is not available."
        raise HTTPException(404, detail=message)

    return FileResponse(plot_path_disk, media_type="image/png",
                        filename=sim_id + "_" + value.value + ".png")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request,
                                        exc: StarletteHTTPException):
    """Handles 404 exceptions by rendering a template."""
    return templates.TemplateResponse(
        "404.html",
        {
            "request": request,
        }
    )

if __name__ == "__main__":
    pass