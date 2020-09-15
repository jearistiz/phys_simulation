from datetime import datetime
import numpy as np


class Simulation():
    """Class: Simulation

    Atributes
    ---------
    ini_cndtn : list
        initial condition of simulation, its specification depends on
        simulation type
    date : datetime

    """
    def __init__(self, ini_cndtn, user_name=None):
        self.ini_cndtn = ini_cndtn
        self.date = datetime.now()
        self.user_name = user_name
        self.sim_type = None


class HarmonicOsc(Simulation):
    pass

print(HarmonicOsc([0,0], "Juan").ini_cndtn)