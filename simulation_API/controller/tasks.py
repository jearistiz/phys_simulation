"""This file will do background tasks e.g. the simulation
"""
import time
from datetime import datetime

from fastapi import Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from simulation_API import app, templates
from simulation_API.config import PATH_PLOTS
import numpy as np 
import matplotlib.pyplot as plt

# Import simulation module
from simulation_API.model.simulation.simulation import HarmonicOsc1D
# Import pydantic model for Harmonic Oscillator request
from simulation_API.controller.schemas import (SimSystem, SimRequest, SimResults,
                                               SimResultsPaths)


def _run_simulation(sim_params: SimRequest) -> SimResultsPaths:
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
    # Finally pop "system" from sim_params, bc we do not need it
    # Remember system will be instance of SimSystem defined in schemas.py
    system = sim_params.pop("system")

    if system.value == SimSystem.ho:
        # Run simulation and get results as returned by scipy.integrate.solve_ivp
        simulation_instance = HarmonicOsc1D(**sim_params)
        simulation = simulation_instance.simulate()
    elif system == SimSystem.qho:
        # Do not run
        sim_results = SimResultsPaths(sim_id=1,
                                      date=datetime.now(),
                                      routes_plots=["Simulation not available", "n/a"],
                                      route_pickle="n/a",
                                      route_results="n/a")                                      
        return sim_results


    # Store simulation parameters in database
    # TODO

    # Store simulation result in pickle
    # TODO

    # Create and save plots
    _plot_solution(SimResults(sim_results=simulation), system)

    # Return paths of simulation results 
    sim_results = SimResultsPaths(sim_id=1,
                                  date=simulation_instance.date,
                                  routes_plots=["hello", "world"],
                                  route_results="hi there",
                                  route_pickle="night night")

    return sim_results


    ##### Try to run simulations via a route 


def _plot_solution(sim_results: SimResults, system: SimSystem) -> None:
    """Plot solutions (initially only harmonic simulator solution)"""
    # Get simulation results as OdeResult instance
    sim_results = sim_results.sim_results

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(sim_results.y[0], sim_results.y[1])
    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('q')
    plt.ylabel('p')
    plt.title('Phase space')
    plt.savefig(PATH_PLOTS + "sol_phase_space.png")
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(sim_results.t, sim_results.y[0], label='q(t)')
    plt.plot(sim_results.t, sim_results.y[1], label='p(t)')
    plt.xlabel('t')
    plt.ylabel('Canonical coordinates evolution')
    plt.title('Solution')
    plt.legend()
    plt.savefig(PATH_PLOTS + "sol_time_series.png")
    plt.close()
    return