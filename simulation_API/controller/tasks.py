"""This file will do background tasks e.g. the simulation
"""
from datetime import datetime
from typing import Optional, Any

from fastapi import Depends
# Database related
from sqlalchemy.orm import Session
# import matplotlib as mpl
from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
import pickle as pkl

# Import app instance
from simulation_API import app
# Import path to save plots
from simulation_API.config import PATH_PLOTS, PATH_PICKLES
# Import simulation module
from simulation_API.model.simulation.simulation import HarmonicOsc1D
# Import pydantic schemas
from .schemas import *
# Database related
from simulation_API.model.db.db_manager import SessionLocal
from simulation_API.model.db import crud, models


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
        if system.value == SimSystem.ho:
            # Run simulation and get results as returned by scipy.integrate.solve_ivp
            simulation_instance = HarmonicOsc1D(**sim_params)
            simulation = simulation_instance.simulate()
        elif system == SimSystem.qho:
            # Quantum Harmonic Oscillator simulation not available
            # Create a simulation status entry for database
            create_simulation_status_db = SimulationDBSchCreate(
                sim_id=sim_id,
                user_id=user_id,
                date=str(datetime.utcnow()),
                system=system,
                success=False,
                message="QHO simulation is not available at the moment"
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
            date=datetime.utcnow(),
            system=system,
            success=False,
            message=str(e)
        )
        crud._create_simulation(db, create_simulation_status_db)
        db.close()
        
        return

    # Store simulation result in pickle
    _pickle(sim_id + ".pickle", PATH_PICKLES, dict(simulation))
    route_pickle = PATH_PICKLES
    
    # Create and save plots
    plot_query_values = _plot_solution(SimResults(sim_results=simulation),
                                       system, PATH_PLOTS, sim_id)

    # Create a simulation status entry for database
    create_simulation_status_db = SimulationDBSchCreate(
        sim_id=sim_id,
        user_id=user_id,
        date=simulation_instance.date,
        system=system,
        method=sim_params["method"],
        route_pickle=_create_pickle_path(sim_id),
        route_results=_create_sim_status_path(sim_id),
        route_plots=_create_plots_path(sim_id),
        success=True,
        message="Finished."
    )
    # Save simulation status in database
    crud._create_simulation(db, create_simulation_status_db)

    # Store simulation parameters in database
    # TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO

    plot_query_values = [
        PlotDBSchCreate(sim_id=sim_id, plot_query_value=plot_qb)
        for plot_qb in plot_query_values
    ]

    crud._create_plot_query_values(db, plot_query_values)

    # Close db session
    db.close()

    return 


def _plot_solution(sim_results: SimResults, system: SimSystem,
                   path: str = '', plot_basename : str = "00000") -> list:
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


def _create_sim_status_path(sim_id: str) -> str:
    """Given simulation id, creates path to access simulation status"""
    return f'/api/results/{sim_id}'


def _create_pickle_path(sim_id: str) -> str:
    return f'/api/results/{sim_id}/pickle'


def _create_plots_path(sim_id: str) -> str:
    return f'/api/results/{sim_id}/plot'


def _create_pickle_path_disk(sim_id: str) -> str:
    return PATH_PICKLES + sim_id + ".pickle"


def _create_plot_path_disk(sim_id: str, query_param: str) -> str:
    return PATH_PLOTS + sim_id + "_" + query_param + ".png"