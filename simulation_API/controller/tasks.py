"""This file will do background tasks e.g. the simulation
"""
from datetime import datetime
from typing import Optional, Any

# import matplotlib as mpl
from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
import pickle as pkl
from numpy import arange

# Import path to save plots
from simulation_API.config import PATH_PLOTS, PATH_PICKLES
# Import simulation module
from simulation_API.model.simulation import Simulations
# Import pydantic schemas
from .schemas import *
# Database related
from simulation_API.model.db.db_manager import SessionLocal
from simulation_API.model.db import crud


"""Next line of code avoids a warning when generating matplotlib figures: 
`UserWarning: Starting a Matplotlib GUI outside of the main thread will likely
fail.`

Found the solution in this post: 
https://stackoverflow.com/questions/50157759/runtimeerror-main-thread-is-not-in-main-loop-using-matplotlib-with-django
The latter cites this matplotlib documentation:
https://matplotlib.org/faq/howto_faq.html#matplotlib-in-a-web-application-server

From last link: 'You may be able to work on separate figures from separate
threads. However, you must in that case use a non-interactive backend
(typically Agg), because most GUI backends require being run from the main
thread as well.'

And also: 'In general, the simplest solution when using
Matplotlib in a web server is to completely avoid using pyplot.'

Next line of code is only needed if using pyplot (which is not recommended)
"""
# mpl.use('Agg')


def _run_simulation(sim_params: SimRequest) -> None: 
    """Run the requested simulation of Harmonic Oscillator

    This function runs the simulation, stores the simulation parameters
    (implicit in `ho_sim`) in a database, stores the simulation result in a
    pickle, creates and saves plots of the simulation and returns
    a dict with paths to download the reslts.

    Parameters
    ----------
    ho_sim : HarmonicOscillator
        pydantic model with all the information needed for the simulation

    Returns
    -------
    """
    # Start session in dbase
    db = SessionLocal()

    # Convert the request type to dict (allows us to provide them as kwargs to HarmonicOsc1D)
    sim_params = sim_params.dict()    

    # Pop "system", "sim_id" and "user_id" from sim_params, bc we do
    # not need to pass them to Simulation class.
    # Remember "system" will be instance of SimSystem defined in schemas.py
    system = sim_params.pop("system")
    sim_id = sim_params.pop("sim_id")
    username = sim_params.pop("username")
    user_id = sim_params.pop("user_id")

    try:
        if (system in SimSystem) and (system != SimSystem.QHO):
            # Run simulation and get results as returned by scipy.integrate.solve_ivp
            LocalSimulation = Simulations[system.value]
            simulation_instance = LocalSimulation(**sim_params)
            simulation = simulation_instance.simulate()
        else:
            create_simulation_status_db = SimulationDBSchCreate(
                sim_id=sim_id,
                user_id=user_id,
                date=str(datetime.utcnow()),
                system=system.value,
                success=False,
                message=na_message
            )
            # Save simulation status in database
            crud._create_simulation(db, create_simulation_status_db)
            # Close db session
            db.close()

            # Exit this function
            return
    
    except Exception as e:
        
        create_simulation_status_db = SimulationDBSchCreate(
            sim_id=sim_id,
            user_id=user_id,
            date=str(datetime.utcnow()),
            system=system.value,
            success=False,
            message=str(e)
        )
        crud._create_simulation(db, create_simulation_status_db)
        db.close()
        
        return

    # Store simulation result in pickle
    _pickle(sim_id + ".pickle", PATH_PICKLES, dict(simulation))
    
    # Create and save plots
    plot_query_values = _plot_solution(SimResults(sim_results=simulation),
                                       system, PATH_PLOTS, sim_id)

    # Save simulation status in database
    create_simulation_status_db = SimulationDBSchCreate(
        sim_id=sim_id,
        user_id=user_id,
        date=simulation_instance.date,
        system=system.value,
        method=sim_params["method"],
        route_pickle=_create_pickle_path(sim_id),
        route_results=_create_sim_status_path(sim_id),
        route_plots=_create_plots_path(sim_id),
        success=True,
        message=sim_status_finished_message
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
                   path: str = '', plot_basename: str = "00000") -> list:
    """Plot solutions. Right now only support Harmonic Oscillator plots"""
    # Get simulation results as OdeResult instance
    
    sim_results = sim_results.sim_results
    plot_query_values = []
    
    ################################
    # Using pyplot (not recommended)
    ################################
    # # Phase space trajectory plot
    # plot_id = 'phase'
    # plot_ids.append(plot_id)

    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # plt.plot(sim_results.y[0], sim_results.y[1])
    # ax.set_aspect('equal', adjustable='box')
    # plt.xlabel('q')
    # plt.ylabel('p')
    # plt.title('Phase space')
    # plt.savefig(PATH_PLOTS + plot_basename + "_" + plot_id + ".png")
    # plt.close()

    # # Canonical coordinates evolution plot
    # plot_id = 'coord'
    # plot_ids.append(plot_id)

    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # plt.plot(sim_results.t, sim_results.y[0], label='q(t)')
    # plt.plot(sim_results.t, sim_results.y[1], label='p(t)')
    # plt.xlabel('t')
    # plt.ylabel('Canonical coordinate')
    # plt.title('Canonical coordinates evolution')
    # plt.legend()
    # plt.savefig(PATH_PLOTS + plot_basename + "_" + plot_id + ".png")
    # plt.close()

    ###########################################################################
    # NOT using pyplot (RECOMMENDED, read comments provided after imports here)
    ###########################################################################

    # Phase space trajectory plot
    plot_query_value = 'phase'
    plot_query_values.append(plot_query_value)

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(sim_results.y[0], sim_results.y[1])
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('q')
    ax.set_ylabel('p')
    ax.set_title('Phase space')
    fig.savefig(PATH_PLOTS + plot_basename + "_" + plot_query_value + ".png")
    

    # Canonical coordinates evolution plot
    plot_query_value = 'coord'
    plot_query_values.append(plot_query_value)

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(sim_results.t, sim_results.y[0], label='q(t)')
    ax.plot(sim_results.t, sim_results.y[1], label='p(t)')
    ax.set_xlabel('t')
    ax.set_ylabel('Canonical coordinate')
    ax.set_title('Canonical coordinates evolution')
    ax.legend()
    fig.savefig(PATH_PLOTS + plot_basename + "_" + plot_query_value + ".png")
    
    return plot_query_values


def _pickle(
    file_name: str, path: str = '', data: Optional[dict] = None
) -> Any:
    """Save data (dictionary format) to or read file from pickle.
    
    Parameters
    ----------
    file_name : str
        Name of file to be read from or to write on.
    path : str
        Path of directory in which file will be saved.
    data : dict or None, optional
        If you want to save data to a pickle, provide the data as dictionary.
        Default is None.
    
    Returns
    -------
    loaded_object : any, optional
        object loaded when no data is provided

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

def _sim_form_to_sim_request(form: Dict[str, str]) -> Optional[SimRequest]:
    t0 = float(form["t0"])
    tf = float(form["tf"])
    
    # Manually check that t0 < tf
    if not t0 < tf:
        return None

    dt = float(form["dt"])
    t_eval = list(arange(t0, tf, dt))

    # Initial conditions
    ini_cndtn_keys = [key for key in form.keys() if key[:3]=="ini"]
    ini_cndtn = [float(form[f"ini{i}"]) for i in range(len(ini_cndtn_keys))]
    
    # Parameters
    # NOTE
    # We need to get the actual names of the parameters, bc the convention in
    # frontend form is `param0`, `param1`, ... but SimRequest receives the
    # actual name of the parameters (e.g. for the HO `m` and `k`)
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
    }

    return SimRequest(**sim_request)


############################## Paths and routes ###############################

def _create_sim_status_path(sim_id: str) -> str:
    """Creates routes to access simulation status by sim_id"""
    return f'/api/results/status/{sim_id}'


def _create_pickle_path(sim_id: str) -> str:
    """Creates routes to download simulation results (pickle) by sim_id"""
    return f'/api/results/{sim_id}/pickle'


def _create_plots_path(sim_id: str) -> str:
    """Creates routes to download plots of simulation results (png) by sim_id"""
    return f'/api/results/{sim_id}/plot'


def _create_pickle_path_disk(sim_id: str) -> str:
    """Creates disk path to simulation results (pickle) by sim_id"""
    return PATH_PICKLES + sim_id + ".pickle"


def _create_plot_path_disk(sim_id: str, query_param: str) -> str:
    """Creates disk path to plots of simulation results (png) by sim_id"""
    return PATH_PLOTS + sim_id + "_" + query_param + ".png"