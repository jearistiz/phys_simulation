from datetime import datetime
import numpy as np


class Simulation:
    """Class: Simulation

    Atributes
    ---------
    ini_cndtn : list
        Initial condition of simulation, its specification depends on
        simulation

    date : datetime
        Date of instantiation of object

    user_name : str
        Name of person that called the simulation
    """
    def __init__(self, ini_cndtn, integration_method = None, user_name=None):
        self.ini_cndtn = ini_cndtn
        self.date = datetime.now()
        self.user_name = user_name
        


class HarmonicOsc(Simulation):
    """Harmonic Oscillator simulation

    Atributes
    ---------
    ini_cndtn : list
        initial condition of simulation, its specification depends on
        simulation
    date : datetime
        date of instantiation of object
    user_name : str
        iame of person that called the simulation
    
    
    Hello
    """
    def __init__(self, ini_cndtn, integration_method=None, user_name=None):
        super().__init__(ini_cndtn, integration_method, user_name)


