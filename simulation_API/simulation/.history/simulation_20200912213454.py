from datetime import datetime
import numpy as np


class Simulation():
    def __init__(self, ini_cndtn, date, user):
        self.ini_cond = ini_cndtn
        self.date = datetime.now()
        self.user = user


class HarmonicOsc(Simulation):
    pass