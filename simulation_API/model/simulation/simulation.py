"""This module simulates mechanical systems"""
from typing import Optional, List, Tuple
from math import pi

from datetime import datetime
from scipy.integrate import solve_ivp
from scipy.integrate._ivp.ivp import OdeResult


class Simulation(object):
    """Simulation of a conservative mechanical system

    Attributes
    ---------
    t_span : list of floats shape (2,) or None
        Interval of integration (t0, tf).
    t_eval : array_like or None
        Times at which to store the computed solution, must be sorted and
        lie within t_span.
    ini_cndtn : array_like or None
        Initial condition of simulation, its specification depends on
        the system being simulated.
    params : dict or None
        Contains all the parameters of the simulation (e.g. for the harmonic
        oscillator `self.params = {"m": 1., "k": 1.}`)
    method : str, optional
        Method of integration.
    user_name : str or None
        Username that called the simulation.
    system : string or None
        Description of simulated system.
    date : datetime.
        UTC date and time of instantiation of object.
    results : Any or None
        Results of simulation.
    """
    system = None
    def __init__(self,
                 t_span: Optional[List[float]] = None,
                 t_eval: Optional[list] = None,
                 ini_cndtn: Optional[list] = None,
                 params: Optional[dict] = None,
                 method: Optional[str] = None,
                 user_name: Optional[str] = None) -> None:
        """
        Parameters
        ----------
        t_span : 2-tuple of floats, optional
            Interval of integration (t0, tf). The solver starts with t=t0 and
            integrates until it reaches t=tf.
        t_eval : array_like or None, optional
            Times at which to store the computed solution, must be sorted and
            lie within t_span. If None (default), use points selected by the
            solver.
        ini_cndtn : list, shape (2,), optional
            Initial condition of simulated system.
        params : dict or None, optional
            Contains all the parameters of the simulation (e.g. the harmonic
            oscillator will contain {"m": 1., "k": 1.})
        method : string, optional
            Method of integration, varies depending on simulation. See
            avaliable methods on `scipy.integrate.solve_ivp` documentation.
            Default is None.
        user_name : string, optional
            Username that called the simulation. Default is None.
        """
        self.t_span = t_span
        self.t_eval = t_eval
        self.ini_cndtn = ini_cndtn
        self.params = params
        self.method = method
        self.user_name = user_name
        self.results = None
        self.date = str(datetime.utcnow())
        


class HarmonicOsc1D(Simulation):
    """1-D Harmonic Oscillator simulation

    Attributes
    ---------
    In addition to Simulation's attributes:

    m : float
        Mass of object.
    k : float
        Force constant of harmonic oscilltor.

    Methods
    -------
    h_eqns(self, t, y):
        Calculates hamilton's equations for 1D-Harmonic Oscillator.
    simulate()
        Simulates 1d harmonic oscillator using `scipy.integrate.solve_ivp`.

    Notes
    -----
    The hamiltonian describing the harmonic oscillator is written as

    .. math::
        
        H = \sqrt{1}{2}p^2 + \sqrt{1}{2}k q^2
    """
    system = "Harmonic-Oscillator"

    def __init__(self,
                 t_span: Optional[Tuple[float, float]] = [0, 2 * pi], 
                 t_eval: Optional[tuple] = None,
                 ini_cndtn: List[float] = [0., 1.],
                 params: dict = {"m": 1., "k": 1.},
                 method: str = 'RK45',
                 user_name: Optional[str] = None) -> None:
        """Extends __init__ from Simulation
        
        Adds attributes `k` and `m` Simulation's attributes.
        
        Parameters
        ----------
        t_span : 2-tuple of floats
            Interval of integration (t0, tf). The solver starts with t=t0 and
            integrates until it reaches t=tf.
        t_eval : array_like or None, optional
            Times at which to store the computed solution, must be sorted and
            lie within t_span. If None (default), use points selected by the
            solver.
        m : float, optional
            Mass of object. Default is 1. 
        k : float, optional
            Force constant of harmonic oscilltor. Default is 1.
        ini_cndtn : array_like, shape (2,)
            Initial condition of 1D Harmonic Oscillator. Convention: [q0, p0].
            Default is [0., 1.]. A list of initial conditions can be used, in 
            this case a list of solutions will be returned by `simulate` method.
        params : dict, optional
            Contains all the parameters of the simulation.
            Default is  {"m": 1., "k": 1.}. Signature must match
                `{
                    "m": float,
                    "k": float,
                }`
        method : str, optional
            Method of integration, varies depending on simulation. See
            avaliable methods on `scipy.integrate.solve_ivp` documentation.
            Default is 'RK45'.
        user_name : str, optional
            Username that called the simulation.
        """
        super().__init__(t_span, t_eval, ini_cndtn, params, method, user_name)
        self.m = params["m"]
        self.k = params["k"]

    def h_eqns(self, t: float, y: List[float]) -> List[float]:
        """Hamilton's equations for 1D-Harmonic Oscillator

        Parameters
        ----------
        t : float
            Time of evaluation of Hamilton's equations.
        y : array_like, shape (2,)
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
        q, p = y
        dydt = [p / self.m, - q * self.k]
        return dydt

    def simulate(self) -> OdeResult:
        """Simulates 1d harmonic oscillator using `scipy.integrate.solve_ivp`
        
        Returns
        -------
        self.results : OdeResult
            Bunch object with the following fields defined:
                t : ndarray, shape (n_points,)
                    Time points.
                y : ndarray, shape (n, n_points)
                    Values of the solution at t.
                sol : OdeSolution or None
                    Found solution as OdeSolution instance; None if 
                    dense_output was set to False.
                t_events : list of ndarray or None
                    Contains for each event type a list of arrays at which an
                    event of that type event was detected. None if events was
                    None.
                y_events : list of ndarray or None
                    For each value of t_events, the corresponding value of the
                    solution. None if events was None.
                nfev : int
                    Number of evaluations of the right-hand side.
                njev : int
                    Number of evaluations of the Jacobian.
                nlu : int
                    Number of LU decompositions.
                status : int
                    Reason for algorithm termination:
                        -1: Integration step failed.
                        0: The solver successfully reached the end of tspan.
                        1: A termination event occurred.
                message : string
                    Human-readable description of the termination reason.
                success : bool
                    True if the solver reached the interval end or a
                    termination event occurred (status >= 0).
        """
        # Update self.results with simulation results
        self.results = solve_ivp(self.h_eqns, self.t_span, self.ini_cndtn,
                                 self.method, self.t_eval)
        return self.results
