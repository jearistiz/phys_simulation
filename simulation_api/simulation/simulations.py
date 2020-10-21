"""This module simulates mechanical systems"""
from typing import Optional, List, Tuple
from math import pi

from datetime import datetime
from scipy.integrate import solve_ivp
from scipy.integrate._ivp.ivp import OdeResult


class Simulation(object):
    """Simulation of a continuous dynamical system described by first order
    coupled differential equations.

    Attributes
    ---------
    t_span : List[float, float] or None
        Interval of integration (t0, tf).
    t_eval : array_like or None
        Times at which to store the computed solution, must be sorted and
        lie within t_span.
    ini_cndtn : array_like or None
        Initial condition of simulation, its specification depends on
        the system being simulated.
    params : dict or None
        Contains all the parameters of the simulation (e.g. for the harmonic
        oscillator ``self.params = {"m": 1., "k": 1.}``)
    method : str, optional
        Method of integration.
    user_name : str or None
        Username that instantiated the simulation.
    date : datetime (str).
        UTC date and time of instantiation of object.
    results : ``scipy.integrate._ivp.ivp.OdeResult`` or None
        Results of simulation.
    """
    system = None
    """Name of system."""
    def __init__(self,
                 t_span: Optional[List[float]] = None,
                 t_eval: Optional[list] = None,
                 ini_cndtn: Optional[list] = None,
                 params: Optional[dict] = None,
                 method: Optional[str] = 'RK45',
                 user_name: Optional[str] = None) -> None:
        """Initializes all :class:`self` attributes except ``self.system``"""
        self.t_span = t_span
        self.t_eval = t_eval
        self.ini_cndtn = ini_cndtn
        self.params = params
        self.method = method
        self.user_name = user_name
        self.results = None
        self.date = str(datetime.utcnow())

    def dyn_sys_eqns(self, t: float, y: List[float]) -> List[float]:
        """Trivial 2D dynamical system. Just for reference.
        
        Note
        ----
        The actual simulations that inherit this class will replace this method
        with the relevant dynamical equations.
        """
        # The vector is decomposed in its phase space variables.
        p, q = y
        
        # Then, the dynamical system is defined. In general, dydt = f(p, q, t)
        # but this is just the trivial dynamical system.
        dydt = [0 * p, 0 * q]
        
        return dydt

    def simulate(self) -> OdeResult:
        """Simulates ``self.system`` abstracted in ``self.dyn_sys_eqns``
        and using ``scipy.integrate.solve_ivp``.
        
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
                    Reason for algorithm termination: -1, Integration step
                    failed; 0, The solver successfully reached the end of
                    tspan; 1, A termination event occurred.
                message : string
                    Human-readable description of the termination reason.
                success : bool
                    True if the solver reached the interval end or a
                    termination event occurred (status >= 0).
        """
        # Update self.results with simulation results
        self.results = solve_ivp(self.dyn_sys_eqns, self.t_span, self.ini_cndtn,
                                 self.method, self.t_eval)
        return self.results
        


class HarmonicOsc1D(Simulation):
    """1-D Harmonic Oscillator simulation

    Attributes
    ---------
    m : float
        Mass of object.
    k : float
        Force constant of harmonic oscilltor.

    Notes
    -----
    The hamiltonian describing the Harmonic Oscillator is defined dy

    .. math::
        
        H = \\frac{1}{2m}p^2 + \\frac{1}{2}k q^2
    """
    system = "Harmonic-Oscillator"

    def __init__(self,
                 t_span: Optional[Tuple[float, float]] = [0, 2 * pi], 
                 t_eval: Optional[tuple] = None,
                 ini_cndtn: List[float] = [0., 1.],
                 params: dict = {"m": 1., "k": 1.},
                 method: str = 'RK45',
                 user_name: Optional[str] = None) -> None:
        """Extends :meth:`Simulation.__init__`
        
        Adds attributes
        :attr:`HarmonicOsc1D.m` and
        :attr:`HarmonicOsc1D.k`.
        
        Parameters
        ----------
        ini_cndtn : array_like, shape (2,)
            Initial condition of 1D Harmonic Oscillator. Convention: 
            :math:`\\texttt{ini_cndtn} = [q_0, p_0]` where :math:`q_0` is the initial
            generalised position and :math:`p_0` is the initial generalised
            momentum. Default is ``[0., 1.]``. A list of initial conditions
            can be used, in this case a list of solutions will be returned by
            :meth:`Simulation.simulate`.
        params : dict, optional
            Contains all the parameters of the simulation. Schema must match::

                {
                    "m": float,     # Mass of object.
                    "k": float,     # Force constant of harmonic oscilltor.
                }
            
            Default is  ``{"m": 1., "k": 1.}``.
        """
        super().__init__(t_span, t_eval, ini_cndtn, params, method, user_name)
        self.m = params["m"]
        self.k = params["k"]

    def dyn_sys_eqns(self, t: float, y: List[float]) -> List[float]:
        """Hamilton's equations for 1D-Harmonic Oscillator.

        Note
        ----
        Overwrites :attr:`Simulation.dyn_sys_eqns`.

        Parameters
        ----------
        t : float
            Time of evaluation of Hamilton's equations.
        y : array_like, shape (2,)
            Canonical coordinates.
            Convention: :math:`\\texttt{y} = [q, p]` where :math:`q` is the
            generalised position and :math:`p` is the generalised momentum.

        Returns
        -------
        dydt : array_like, shape (2,)
            Hamilton's equations for 1D Harmonic Oscillator.
            :math:`\\texttt{dydt} = \left[ \\frac{dq}{dt}, \\frac{dp}{dt} \\right] =
            \left[ \\frac{\partial H}{\partial p}, - \\frac{\partial H}{\partial q} \\right]`
        """
        q, p = y
        dydt = [p / self.m, - q * self.k]
        return dydt




class ChenLeeAttractor(Simulation):
    """Simulates Chen-Lee Attractor.
    

    Attributes
    ----------
    a : float
        :math:`\omega_x` parameter.
    b : float
        :math:`\omega_y` parameter.
    c : float
        :math:`\omega_z` parameter.

    Notes
    -----
    The Chen-Lee Attractor is a dynamical system defined by:[#]_
    
    .. math::
        
        \\frac{d\omega_x}{dt} &= - \omega_y \omega_z + a \, \omega_x

        \\frac{d\omega_y}{dt} &= \omega_z \omega_x + b \, \omega_y
        
        \\frac{d\omega_z}{dt} &= \\frac{1}{3} \omega_x \omega_y + c \, \omega_z  

    Its origin is closely related to the motion of a rigid body in a rotating
    frame of reference.

    References
    ----------
    .. [#] https://doi.org/10.1142/S0218127403006509
    """
    system = "Chen-Lee-Attractor"

    def __init__(self,
                 t_span: Optional[Tuple[float, float]] = [0, 400], 
                 t_eval: Optional[tuple] = None,
                 ini_cndtn: List[float] = [10., 10., 0.,],
                 params: dict = {"a": 3., "b": - 5., "c": - 1.},
                 method: str = 'RK45',
                 user_name: Optional[str] = None) -> None:
        """Extends :meth:`Simulation.__init__`
        
        Adds attributes
        :attr:`ChenLeeAttractor.a`,
        :attr:`ChenLeeAttractor.b` and
        :attr:`ChenLeeAttractor.c`.
        
        Parameters
        ----------
        ini_cndtn : array_like, shape (3,)
            Initial condition of 1D Harmonic Oscillator. Convention: 
            :math:`\\texttt{ini_cndtn} = [\omega_{x0}, \omega_{y0}, \omega_{z0}]`.
            Default is ``[10, 10, 0]``. A list of initial conditions can be
            used, in this case a list of solutions will be returned by
            :py:meth:`Simulation.simulate`
        params : dict, optional
            Contains all the parameters of the simulation. Schema must match::
            
                {
                    "a": float,     # `\omega_x` parameter.
                    "b": float,     # `\omega_x` parameter.
                    "c": float,     # `\omega_z` parameter.
                }

            Default is  ``{"a": 3.0, "b": - 5.0, "c": - 1.0}``.
        """
        super().__init__(t_span, t_eval, ini_cndtn, params, method, user_name)
        self.a = params["a"]
        self.b = params["b"]
        self.c = params["c"]
    
    def dyn_sys_eqns(self, t: float, w: List[float]) -> List[float]:
        """Chen-Lee Dynamical system definition
        
        Note
        ----
        Overwrites :attr:`Simulation.dyn_sys_eqns`.

        Parameters
        ----------
        w : array_like, shape (3,)
            Vector of angular velocity.
            Convention: :math:`\\texttt{w} = [\omega_x, \omega_y, \omega_z]`.
        t : float
            Time.
        
        Returns
        -------
        dwdt : array_like, shape (3,)
            Dynamical system equations of Chen Lee attractor evaluated at ``w``.
        """
        wx, wy, wz = w
        dwdt = [
            - wy * wz + self.a * wx,
            wz * wx + self.b * wy,
            (wx * wy / 3.) + self.c * wz,
        ]
        return dwdt


# NOTE Update this dict with all available simulations
Simulations = {
    HarmonicOsc1D.system: HarmonicOsc1D,
    ChenLeeAttractor.system: ChenLeeAttractor,
}
"""Maps the names of the available systems to their corresponding classes.

Warning
-------
Must be updated each time a new simulation is added (add the new relevant item
to the dictionary).
"""