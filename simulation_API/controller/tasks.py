"""This file will do background tasks e.g. the simulation
"""
import time
from datetime import datetime
from typing import Optional, Any

from fastapi import Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
import numpy as np 
import matplotlib as mpl
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt
import pickle as pkl

# Import app instance
from simulation_API import app
# Import path to save plots
from simulation_API.config import PATH_PLOTS, PATH_PICKLES
# Import simulation module
from simulation_API.model.simulation.simulation import HarmonicOsc1D
# Import pydantic model for Harmonic Oscillator request
from simulation_API.controller.schemas import (SimSystem, SimRequest,
                                               SimStatus, SimResults)


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

    # Convert the request type to dict (allows us to provide them as kwargs to HarmonicOsc1D)
    sim_params = sim_params.dict()
    
    # Pop "system", "sim_id" and "user_id" from sim_params, bc we do
    # not need them Remember "system" will be instance of SimSystem defined in
    # schemas.py
    system = sim_params.pop("system")
    sim_id = sim_params.pop("sim_id")
    user_id = sim_params.pop("user_id")

    # Store simulation parameters in database ???
    # TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO

    try:
        if system.value == SimSystem.ho:
            # Run simulation and get results as returned by scipy.integrate.solve_ivp
            simulation_instance = HarmonicOsc1D(**sim_params)
            simulation = simulation_instance.simulate()
        elif system == SimSystem.qho:
            # Quantum Harmonic Oscillator simulation not available
            sim_status = SimStatus(user_id=user_id,
                                   sim_id=sim_id,
                                   date=datetime.now(),
                                   system=system,
                                   status=False,
                                   message="Not Available")
            return sim_status
    
    except Exception as e:
        
        # Store error message in database
        # TODO TODO TODO TODO TODO TODO Change this when dbase is added
        # TODO TODO TODO TODO TODO TODO Change this when dbase is added
        # TODO TODO TODO TODO TODO TODO Change this when dbase is added
        
        return SimStatus(sim_id=sim_id, user_id=user_id, date=datetime.now(),
                         system=system, status=False,
                         message=str(e))

    # Store simulation result in pickle
    _pickle(sim_id + ".pickle", PATH_PICKLES, dict(simulation))
    route_pickle = PATH_PICKLES

    # Create and save plots
    plot_query_values = _plot_solution(SimResults(sim_results=simulation),
                              system, PATH_PLOTS, sim_id)

    # Save simulation status
    # TODO TODO TODO TODO TODO TODO   Change this when dbase is added
    # TODO TODO TODO TODO TODO TODO   Change this when dbase is added
    # TODO TODO TODO TODO TODO TODO   Change this when dbase is added
    sim_status = SimStatus(sim_id=sim_id,
                           user_id=user_id,
                           date=simulation_instance.date,
                           system=system,
                           ini_cndtn=sim_params["ini_cndtn"],
                           params=sim_params["params"],
                           method=sim_params["method"],
                           route_pickle="morning morning",
                           route_results="hi there",
                           route_plots=["hello", "world"],
                           plot_query_values=plot_query_values,
                           status=True,
                           message="Finished")

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
