from datetime import datetime
from scipy.integrate import solve_ivp


class Simulation(object):
    """Simulation of mechanical system

    Attributes
    ---------
    t_span : 2-tuple of floats
        Interval of integration (t0, tf). The solver starts with t=t0 and
        integrates until it reaches t=tf.
    t_eval : array_like or None, optional
        Times at which to store the computed solution, must be sorted and
        lie within t_span. If None (default), use points selected by the
        solver.
    ini_cndtn : list
        Initial condition of simulation, its specification depends on
        the system being simulated.
    date : datetime
        Date of instantiation of object.
    user_name : str, optional
        Username that called the simulation.
    """
    def __init__(self, t_span, t_eval, ini_cndtn=None,
                 method='RK45', user_name=None):
        """
        Parameters
        ----------
        t_span : 2-tuple of floats
            Interval of integration (t0, tf). The solver starts with t=t0 and
            integrates until it reaches t=tf.
        t_eval : array_like or None, optional
            Times at which to store the computed solution, must be sorted and
            lie within t_span. If None (default), use points selected by the
            solver.
        ini_cndtn : list
            Initial condition of simulation, its specification depends on
            the system being simulated.
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
    def __init__(self, t_span, t_eval, m=1., k=1., ini_cndtn=[0., 1.],
                 method='RK45', user_name=None):
        """Extends __init__ from Simulation
        
        Adds attributes `k` and `m` Simulation's attributes.
        
        Parameters
        ----------
        m : float
            Mass of object. Default is 1. 
        k : float, optional
            Force constant of harmonic oscilltor. Default is 1.
        ini_cndtn : list, len=2
            Initial condition of 1D Harmonic Oscillator. Convention: [q0, p0].
            Default is [0., 1.]
        """
        super().__init__(t_span, t_eval, ini_cndtn, method, user_name)
        self.m = m
        self.k = k

    def h_eqns(self, t, y, m=self.m, k=self.k):
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
        # Update attributes
        self.m, self.k = m, k
        q, p = y
        dydt = [p / m, - q * k]
        return dydt

    def simulate(self):
        return 
