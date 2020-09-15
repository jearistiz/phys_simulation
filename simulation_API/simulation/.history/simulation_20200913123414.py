from datetime import datetime
import numpy as np


class Simulation(object):
    """Class: Simulation

    Attributes
    ---------
    ini_cndtn : list
        Initial condition of simulation, its specification depends on
        the system being simulated.
    date : datetime
        Date of instantiation of object.
    method : str, optional
        Method of integration, varies depending on simulation. See
        avaliable methods on `scipy.integrate.solve_ivp` documentation.
        Default is 'RK45'.
    user_name : str, optional
        Username that called the simulation.
    """
    def __init__(self, ini_cndtn=None, method=None, user_name=None):
        """
        Parameters
        ----------
        ini_cndtn : list
            Initial condition of simulation, its specification depends on
            the system being simulated.
        date : datetime
            Date of instantiation of object.
        method : str, optional
            Method of integration, varies depending on simulation. See
            avaliable methods on `scipy.integrate.solve_ivp` documentation.
            Default is 'RK45'.
        user_name : str, optional
            Username that called the simulation.
        """
        self.ini_cndtn = ini_cndtn
        self.method = method
        self.date = datetime.now()
        self.user_name = user_name
        


class HarmonicOsc1D(Simulation):
    """One-dimensional Harmonic Oscillator simulation

    Attributes
    ---------
    In addition to Simulation's attributes:

    m : float
        Mass of object.
    k : float
        Force constant of harmonic oscilltor.

    Methods
    -------

    Notes
    -----
    The hamiltonian describing the harmonic oscillator is written as

    .. math::
        
        H = \sqrt{1}{2}p^2 + \sqrt{1}{2}k q^2

    
    """
    def __init__(self, ini_cndtn, m=1., k=1., method=None, user_name=None):
        """Extends __init__ from Simulation
        
        Adds attributes `k` and `` to bunch of Simulation's attributes.
        
        Parameters
        ----------
        m : float
            Mass of object. Default is 1. 
        k : float, optional
            Force constant of harmonic oscilltor. Default is 1. 
        """
        super().__init__(ini_cndtn=[0,1], method, user_name)
        self.m = m
        self.k = k

    def h_eqns(self, t, y, m=self.m, k=self.k):
        """Hamilton's equations for 1D-Harmonic Oscillator

        Parameters
        ----------
        t : float
            Time.
        y : list or ndarray
            Canonical coordinates. Convention: [q, p].
        m : float
            Mass of object. Default is `self.m`. 
        k : float, optional
            Force constant of harmonic oscilltor. Default is `self.k`. 

        Returns
        -------
        dydt : list
            Hamilton's equations for 1d Harmonic Oscillator.
            dydt = [dqdt, dpdt] = [dHdp, - dHdq]
        """
        # Update attributes
        self.m, self.k = m, k
        q, p = y
        dydt = [p / m, - q * k]
        return dydt

    def simulate(self):
        return
