from datetime import datetime
import numpy as np


class Simulation():
    def __init__(self, ini_cond, date, user):
        self.ini_cond = None
        self.date = 