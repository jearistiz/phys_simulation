"""This file will do background tasks e.g. the simulation"""
from typing import Optional, Any, List
from datetime import datetime
from uuid import uuid4

# Needed to simulate in backgroung
from fastapi import BackgroundTasks, HTTPException
# Database-related
from sqlalchemy.orm import Session
import matplotlib as mpl
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
import pickle as pkl
from numpy import linspace, abs

from simulation_api import app
# Import pydantic schemas
from .schemas import *
# Import paths to save plots and pickles
from simulation_api.config import PATH_PLOTS, PATH_PICKLES, PLOTS_FORMAT
# Import simulation module
from simulation_api.simulation.simulations import Simulations
# Database-related
from simulation_api.model.db_manager import SessionLocal
from simulation_api.model import crud

# Next line of code avoids a warning when generating matplotlib figures: 
# `UserWarning: Starting a Matplotlib GUI outside of the main thread will likely
# fail.`

# Found the solution in this post: 
# https://stackoverflow.com/questions/50157759/runtimeerror-main-thread-is-not-in-main-loop-using-matplotlib-with-django
# The latter cites this matplotlib documentation:
# https://matplotlib.org/faq/howto_faq.html#matplotlib-in-a-web-application-server

# From last link: 'You may be able to work on separate figures from separate
# threads. However, you must in that case use a non-interactive backend
# (typically Agg), because most GUI backends require being run from the main
# thread as well.'

# And also: 'In general, the simplest solution when using
# Matplotlib in a web server is to completely avoid using pyplot.'

# Next line of code is only needed if using pyplot (which is not recommended)

# mpl.use('Agg')

def _api_simulation_request(sim_system: SimSystem,
                            sim_params: SimRequest,
                            background_tasks: BackgroundTasks,
                            db: Session) -> SimIdResponse:
    """Requests simulation to BackgroundTasks.

    Parameters
    ----------
    sim_system : SimSystem
        System to be simulated.
    sim_params : SimRequest
        Contains all the information about the simulation request.
    background_tasks : ``fastapi.BackgroundTasks``
        Object needed to request simulation in the background.
    db : ``sqlalchemy.orm.Session``
        Needed for interaction with database.
    
    Returns
    -------
    sim_id_response : SimIdResponse
        Contains information about simulation request, such as simulation ID
        and others. See
        :class:`~simulation_api.controller.schemas.SimIdResponse` for more
        information.
    """
    
    ########################## Check for some errors ##########################
    # Check that the simulation parameters are the ones needed for the
    # requested simulation. This is not checked by the pydantic model.
    error_message = ""
    try:
        ParamsModel = SimSystem_to_SimParams[sim_system.value]
        ParamsModel(**sim_params.params)
    except:
        error_message = "Error: you provided the wrong set of parameters. " \
                        "Your simulation was not requested."

    # Check Chen-Lee parameters
    if sim_system.value == SimSystem.ChenLee.value and not error_message:
        params = sim_params.params
        if not _check_chen_lee_params(params["a"], params["b"], params["c"]):
            error_message = "Chen-Lee parameters must satisfy a > 0, and " \
                            "b < 0, and c < 0 and a < -(b + c)"

    if error_message:
        sim_id_response = SimIdResponse(
            username=sim_params.username,
            message=error_message
        )
        return sim_id_response
    ############################## End of check ###############################

    # Create user in database (meanwhile)
    # FIXME FIXME FIXME
    # In production user can NOT be created here, login will be required.
    user = UserDBSchCreate(username=sim_params.username)
    user = crud._create_user(db, user)
    # Get user_id from user and store it in sim params !
    sim_params.user_id = user.user_id

    # Create an id for the simulation store it in hex notation
    sim_params.sim_id = uuid4().hex

    # Close ccurrent db connection, so that _run_simulation can update table
    db.close()

    # Check that the client is accessing the right path for the right simulation
    # sim_system.value NEEDS to match the request given in JSON as
    # sim_params.system
    if not sim_system.value == sim_params.system.value:
        raise HTTPException(
            status_code=403,
            detail=r"403 - Forbidden : URI's {sim_system} value must coincide "
                   r"with 'system' key value in posted JSON file"
        )

    # Simulate system in BACKGROUND
    # TODO TODO TODO Por dentro _run_simulation puede abrir un websocket para
    # TODO TODO TODO indicar que la simulación ya se completó
    background_tasks.add_task(_run_simulation, sim_params)

    # Declare some variables needed as params to SimIdResponse
    sim_status_path = app.url_path_for("api_simulate_status",
                                       sim_id=sim_params.sim_id)
    
    sim_pickle_path = app.url_path_for("api_download_pickle",
                                       sim_id=sim_params.sim_id)

    message1 = "(When –and if– available) request via GET your simulation's" \
               "status in route 'sim_status_path' or download your results" \
               "(pickle fomat) via GET in route 'sim_pickle_path'"
    message2 = na_message
    message = message1 if sim_params.system in SimSystem else message2

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


# NOTE Maybe this function is overloaded, we could split some of the tasks
# maybe its ok, just consider it
def _run_simulation(sim_params: SimRequest) -> None: 
    """Runs the requested simulation and stores the outcome in a database.

    This function runs the simulation, stores the simulation parameters in a
    database, stores the simulation result in a pickle and creates and saves
    relevant plots of the simulation.

    Parameters
    ----------
    sim_params : SimRequest
        Contains all the information needed for the simulation.

    Returns
    -------
    None
    """
    # Start session in dbase
    db = SessionLocal()

    # If t_steps is provided in sim_params, generate t_eval
    if sim_params.t_steps:
        sim_params.t_eval = linspace(
            sim_params.t_span[0], sim_params.t_span[1], sim_params.t_steps
        )

    # Convert the SimRequest instance to dict
    sim_params = sim_params.dict()

    # Pop some values Simulation __init__ method does not accept.
    # Remember "system" will be a member of SimSystem defined in simulation_api.controll.schemas
    system = sim_params.pop("system")
    sim_id = sim_params.pop("sim_id")
    user_id = sim_params.pop("user_id")
    sim_params.pop("t_steps")
    sim_params.pop("username")

    basic_info = {
        "sim_id": sim_id,
        "user_id": user_id,
        "date": str(datetime.utcnow()),
        "system": system.value,
    }

    # Check that "system" is in available simulation systems
    # NOTE maybe this is not necessary since pydantic already checks this. In
    # schema request SimRequest requires "system" to be a member of SimSystem.
    if not system in SimSystem:
        create_simulation_status_db = SimulationDBSchCreate(
            success=False,
            message=na_message,
            **basic_info
        )
        # Save simulation status in database
        crud._create_simulation(db, create_simulation_status_db)
        # Close db session
        db.close()
        return

    # Try to simulate the system. If there is an exception in simulation store
    # it in database and exit this function
    try:        
        # Run simulation and get results as returned by scipy.integrate.solve_ivp
        LocalSimulation = Simulations[system.value]
        simulation_instance = LocalSimulation(**sim_params)
        simulation = simulation_instance.simulate()
    except Exception as e:
        create_simulation_status_db = SimulationDBSchCreate(
            success=False,
            message="Internal Simulation Error: " + str(e),
            **basic_info
        )
        crud._create_simulation(db, create_simulation_status_db)
        db.close()
        
        # FIXME FIXME FIXME is it better to raise an exception at this point?
        return

    # Store simulation result in pickle
    _pickle(sim_id + ".pickle", PATH_PICKLES, dict(simulation))
    
    # Create and save plots
    plot_query_values = _plot_solution(SimResults(sim_results=simulation),
                                       system, sim_id)

    # Save simulation status in database
    create_simulation_status_db = SimulationDBSchCreate(
        method=sim_params["method"],
        route_pickle=app.url_path_for("api_download_pickle", sim_id=sim_id),
        route_results=app.url_path_for("api_simulate_status", sim_id=sim_id),
        route_plots= app.url_path_for("api_download_plots", sim_id=sim_id),
        success=True,
        message=sim_status_finished_message,
        **basic_info
    )
    crud._create_simulation(db, create_simulation_status_db)

    #  Save plot query values to database
    plot_query_values = [
        PlotDBSchCreate(sim_id=sim_id, plot_query_value=plot_qb)
        for plot_qb in plot_query_values
    ]
    crud._create_plot_query_values(db, plot_query_values)

    # Store simulation parameters in database
    parameters = []
    for key, value in simulation_instance.params.items():
        parameter = ParameterDBSchCreate(sim_id=sim_id,
                                         param_type=ParamType.param.value,
                                         param_key=key, value=value)
        parameters.append(parameter)
    for i, ini_cndtn_val in enumerate(simulation_instance.ini_cndtn):
        ini_cndtn = ParameterDBSchCreate(sim_id=sim_id,
                                         param_type=ParamType.ini_cndtn,
                                         ini_cndtn_id=i, value=ini_cndtn_val)
        parameters.append(ini_cndtn)
    crud._create_parameters(db, parameters)
    
    # Close db session
    db.close()

    return 


def _plot_solution(sim_results: SimResults, system: SimSystem,
                   plots_basename: str = "00000") -> List[str]:
    """Generates relevant simulation's plots and saves them.
    
    Parameters
    ----------
    sim_results : SimResults
        Simulation results as returned by
        :meth:`~simulation_api.simulation.simulations.Simulation.simulate`.
    system : SimSystem
        System to be simulated.
    plots_basename : str
        Base name of the plots. Actual name of each plot will be
        ``<plotbasename>_<plot_query_value>.png``, where ``<plot_query_value>``
        is a special tag for each type of plot. In this API, baseplot will
        always be the value of
        :attr:`~simulation_api.controller.schemas.SimIdResponse.sim_id`.

    Returns
    -------
    plot_query_values : List[str]
        Names of each type of plot. These are very important since they are
        needed to access the plots in the API route (these are the possible
        values for the query param "value" in route
        ``/api/results/{sim_id}/plot``).
    """
    
    font_normal_size = 17
    mpl.rcParams.update({'font.size': font_normal_size})

    # Get simulation results as OdeResult instance
    sim_results = sim_results.sim_results
    
    plot_query_values = []

    if system == SimSystem.HO:    
        ##################################
        # Using pyplot (not recommended) #
        ##################################
        # # Phase space trajectory plot
        # plot_query_value = 'phase'
        # plot_query_values.append(plot_query_value)

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # plt.plot(sim_results.y[0], sim_results.y[1])
        # ax.set_aspect('equal', adjustable='box')
        # plt.xlabel('q')
        # plt.ylabel('p')
        # plt.title('Phase space')
        # fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))
        # plt.close()

        # # Canonical coordinates evolution plot
        # plot_query_value = 'coord'
        # plot_query_values.append(plot_query_value)

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # plt.plot(sim_results.t, sim_results.y[0], label='q(t)')
        # plt.plot(sim_results.t, sim_results.y[1], label='p(t)')
        # plt.xlabel('t')
        # plt.ylabel('Canonical coordinate')
        # plt.title('Canonical coordinates evolution')
        # plt.legend()
        # fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))
        # plt.close()

        #######################################################################
        # NOT using pyplot (RECOMMENDED, read comments provided after imports)#
        #######################################################################

        ##################### Phase space trajectory plot #####################
        plot_query_value = PlotQueryValues_HO.phase.value
        plot_query_values.append(plot_query_value)

        xlim = max(abs(sim_results.y[0]))
        ylim = max(abs(sim_results.y[1]))
        ax_lim = max([xlim, ylim]) * 1.05
        dashed_line = [[-ax_lim, ax_lim], [0, 0]]

        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(sim_results.y[0], sim_results.y[1])
        ax.plot(dashed_line[0], dashed_line[1], 'k--')
        ax.plot(dashed_line[1], dashed_line[0], 'k--')
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel('q')
        ax.set_ylabel('p')
        # ax.set_title('Phase space')
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)
        fig.tight_layout()
        fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))
        

        ################ Canonical coordinates evolution plot #################
        plot_query_value = PlotQueryValues_HO.coord.value
        plot_query_values.append(plot_query_value)

        fig = Figure()

        ax = fig.add_subplot(111)
        ax.plot(sim_results.t, sim_results.y[0], label='q(t)')
        ax.plot(sim_results.t, sim_results.y[1], label='p(t)')
        ax.set_xlabel('t')
        ax.set_ylabel('Canonical coordinate')
        ax.legend()

        fig.tight_layout()
        fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))
    
    elif system == SimSystem.ChenLee:
        
        ########################## 3D Phase portrait ##########################
        plot_query_value = PlotQueryValues_ChenLee.threeD.value
        plot_query_values.append(plot_query_value)
        
        # Plot limits
        limx_max = max(sim_results.y[0])
        limx_min = min(sim_results.y[0])
        margin_x = 0.05 * (limx_max - limx_min)
        limy_max = max(sim_results.y[1])
        limy_min = min(sim_results.y[1])
        margin_y = 0.05 * (limy_max - limy_min)
        limz_max = max(sim_results.y[2])
        limz_min = min(sim_results.y[2])
        margin_z = 0.05 * (limz_max - limz_min)
        xlim = (limx_min - margin_x, limx_max + margin_x)
        ylim = (limy_min - margin_y, limy_max + margin_y)
        zlim = (limz_min - margin_z, limz_max + margin_z)

        fig = Figure() # figsize=(12,10))
        ax = fig.gca(projection='3d')    #Parametric 3D curve
        ax.plot(
            sim_results.y[0],
            sim_results.y[1],
            sim_results.y[2],
            c='navy'
        )
        ax.set_xlabel('$\Omega_x$')
        ax.set_ylabel('$\Omega_y$')
        ax.set_zlabel('$\Omega_z$')
        ax.set_zlim(*zlim)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        fig.tight_layout()
        fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))

        ##################### Phase portrait projections ######################
        mpl.rcParams.update({'font.size': 25})

        plot_query_value = PlotQueryValues_ChenLee.project.value
        plot_query_values.append(plot_query_value)

        nrows = 1
        ncols = 3

        fig = Figure(figsize=(20,10))
        
        ax = fig.add_subplot(nrows, ncols, 1)
        ax.plot(
            sim_results.y[0],
            sim_results.y[1],
            label='Phase portrait $\Omega_x\Omega_y$',
            c='indianred'
        )
        ax.legend(loc='best')
        ax.set_xlabel('$\Omega_x$')
        ax.set_ylabel('$\Omega_y$')
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        
        ax = fig.add_subplot(nrows, ncols, 2)
        ax.plot(
            sim_results.y[1],
            sim_results.y[2],
            label='Phase portrait $\Omega_y\Omega_z$',
            c='navy'
        )
        ax.legend(loc='best')
        ax.set_xlabel('$\Omega_y$')
        ax.set_ylabel('$\Omega_z$')
        ax.set_xlim(*ylim)
        ax.set_ylim(*zlim)
        
        ax = fig.add_subplot(nrows, ncols, 3)
        ax.plot(
            sim_results.y[0],
            sim_results.y[2],
            label='Phase portrait $\Omega_x\Omega_z$',
            c='olive'
        )
        ax.legend(loc='best')
        ax.set_xlabel('$\Omega_x$')
        ax.set_ylabel('$\Omega_z$')
        ax.set_xlim(*xlim)
        ax.set_ylim(*zlim)
        
        fig.tight_layout()
        fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))

        mpl.rcParams.update({'font.size': 17})
    
    return plot_query_values


def _pickle(file_name: str, path: str = '',
            data: Optional[dict] = None) -> Any:
    """Saves ``data`` to pickle or reads Python object from pickle.
    
    Saves ``data`` to pickle if ``data``. Otherwise it will try to read a
    pickle from ``path + '/' + file_name`` and return the python object stored
    in it.
    

    Parameters
    ----------
    file_name : str
        Name of file to be read from or to write on.
    path : str
        Path of directory in which the file will be saved or read from.
    data : dict or None, optional
        If you want to save data to a pickle, provide the data as dictionary.
        Default is None.
    
    Returns
    -------
    loaded_object : Any or None
        Object loaded when no data is provided.

    """
    # Set mode to read or write
    mode = "wb" if data else "rb"

    with open(path + file_name, mode) as file:        
        if data:
            pkl.dump(data, file)
            loaded_object = None
        else:
            loaded_object = pkl.load(file)

    return loaded_object


def _sim_form_to_sim_request(form: Dict[str, str]) -> SimRequest:
    """Translates simulation form –from frontend– to simulation request which
    is understood by backend in
    :func:`_api_simulation_request`.

    Parameters
    ----------
    form: Dict[str, str]
        Simulation request information as obtained by frontend.

    Returns
    -------
    SimRequest
        Simulation request information in a format the backend understands.
    """
    # Generate t_eval
    t0 = float(form["t0"])
    tf = float(form["tf"])
    t_steps = int(form["t_steps"])
    if t_steps:
        t_eval = list(linspace(t0, tf, t_steps))
    else:
        dt = float(form["dt"])
        t_eval = list(linspace(t0, tf, int((tf - t0) / dt)))

    # Initial conditions
    ini_cndtn_keys = [key for key in form.keys() if key[:3]=="ini"]
    ini_cndtn = [float(form[f"ini{i}"]) for i in range(len(ini_cndtn_keys))]
    
    # Parameters
    # NOTE
    # We need to get the actual names of the parameters, because the convention
    # in frontend form is `param0`, `param1`, ... but SimRequest receives the
    # actual name of the parameters (e.g. for the HO `m` and `k`).
    # This change of convention is done by the dicts defined in `shcemas.py`
    param_convention = system_to_params_dict[form["sim_sys"]]
    param_keys = [key for key in form.keys() if key[:5]=="param"]
    params = {
        param_convention[f"param{i}"]: float(form[f"param{i}"]) 
            for i in range(len(param_keys))
    }

    sim_request = {
        "system": form["sim_sys"],
        "t_span": [t0, tf],
        "t_eval": t_eval,
        "ini_cndtn": ini_cndtn,
        "params": params,
        "method": form["method"],
        "username": form["username"],
        "sim_request": True
    }
    
    return SimRequest(**sim_request)


############################## Paths and routes ###############################

def _create_pickle_path_disk(sim_id: str) -> str:
    """Creates disk path to simulation results (pickle) by
    :attr:`~simulation_api.controller.schemas.SimIdResponse.sim_id`."""
    return PATH_PICKLES + sim_id + ".pickle"


def _create_plot_path_disk(sim_id: str, query_param: PlotQueryValues,
                           plot_format: str = PLOTS_FORMAT) -> str:
    """Creates disk path to plots of simulation results by
    :attr:`~simulation_api.controller.schemas.SimIdResponse.sim_id`."""
    return PATH_PLOTS + sim_id + "_" + query_param + plot_format


########################## Check Chen-Lee Parameters ##########################

def _check_chen_lee_params(a: float, b:float, c: float):
    """Checks that the set of Chen-Lee parameters satisfy chaotic conditions, 
    therefore bound solutions.

    The conditions are

    .. math::

        a > 0 \,\\text{ and }\, b < 0 \,\\text{ and }\, c < 0 \,\\text{ and }\, a < - (b + c)

    Note
    ----
    This conditions are stated in `this reference`_.
    
    .. _this reference: https://doi.org/10.1142/S0218127403006509

    Parameters
    ----------
    a : float
        :math:`\omega_x` parameter.
    b : float
        :math:`\omega_y` parameter.
    c : float
        :math:`\omega_z` parameter.
    """ 
    return (a > 0) and (b < 0) and (c < 0) and (a < - (b + c))
