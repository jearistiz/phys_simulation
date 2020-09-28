"""Test for simulations defined in simulation module
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from time import time

from simulation import ChenLeeAttractor, HarmonicOsc1D

HO = False
ChenLee = True

if HO:
    # Number of time steps for simulation
    t_steps = 100

    # Parameters of simulation
    t_span = [0, 2 * np.pi]
    t_eval = list(np.linspace(t_span[0], t_span[-1], t_steps))
    m, k = 1, 1
    params = {"m": m, "k": k}
    ini_cndtn = [1., 0.]
    method = 'RK45'
    user_name = 'Juan'

    t_0 = time()
    # HarmonicOsc1D object with specified parameters of simulation
    HO_simulation = HarmonicOsc1D(t_span, t_eval, ini_cndtn, params, method,
                                user_name)

    # Simulate 1d-HO
    HO_solution = HO_simulation.simulate()
    t_1 = time()

    # Print some of the attributes of the simulation
    print("Method:", HO_simulation.method)
    print("Date:", HO_simulation.date)
    print("User:", HO_simulation.user_name)
    print(f"Simulation time: {t_1 - t_0:.4f} seconds")

    # Plot solution

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(HO_solution.y[0], HO_solution.y[1])
    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('q')
    plt.ylabel('p')
    plt.title('Phase space')
    plt.show()
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(HO_solution.t, HO_solution.y[0], label='q(t)')
    plt.plot(HO_solution.t, HO_solution.y[1], label='p(t)')
    plt.xlabel('t')
    plt.ylabel('Canonical coordinate')
    plt.title('Solution')
    plt.legend()
    plt.show()
    plt.close()

if ChenLee:
    # Number of time steps for simulation
    t_steps = 10000
    trans_steps = int(0. * t_steps)

    # Parameters of simulation
    t_span = [0, 100]
    t_eval = list(np.linspace(t_span[0], t_span[-1], t_steps))
    a, b, c = 3., -5., -1.
    params = {"a": a, "b": b, "c": c}
    ini_cndtn = [10., 10., 0.]
    method = 'RK45'
    user_name = 'Juan'

    t_0 = time()
    # HarmonicOsc1D object with specified parameters of simulation
    ChenLee_simulation = ChenLeeAttractor(t_span, t_eval, ini_cndtn, params,
                                          method, user_name)

    # Simulate 1d-HO
    ChenLee_solution = ChenLee_simulation.simulate()
    t_1 = time()

    # Print some of the attributes of the simulation
    print("Method:", ChenLee_simulation.method)
    print("Date:", ChenLee_simulation.date)
    print("User:", ChenLee_simulation.user_name)
    print(f"Simulation time: {t_1 - t_0:.4f} seconds")

    # Plot limits
    limx = 1.05 * max(np.abs(ChenLee_solution.y[0][trans_steps:]))
    limy = 1.05 * max(np.abs(ChenLee_solution.y[1][trans_steps:]))
    limz = 1.05 * max(np.abs(ChenLee_solution.y[2][trans_steps:]))
    xlim = (-limx, limx)
    ylim = (-limy, limy)
    zlim = (0, limz)

    fig = plt.figure() # figsize=(12,10))
    ax = fig.gca(projection='3d')    #Parametric 3D curve
    ax.plot(
        ChenLee_solution.y[0][trans_steps:],
        ChenLee_solution.y[1][trans_steps:],
        ChenLee_solution.y[2][trans_steps:]
    )
    ax.set_title('Chen-Lee Attractor')
    ax.set_xlabel( '$\Omega_x$' )
    ax.set_ylabel( '$\Omega_y$' )
    ax.set_zlabel( '$\Omega_z$' )
    ax.set_zlim(*zlim)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    plt.show()