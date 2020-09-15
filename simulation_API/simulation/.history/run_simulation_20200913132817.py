import numpy as np

from simulation import HarmonicOsc1D


t_span = (0, 3)
t_eval = np.lins

simulation = HarmonicOsc1D(t_span, t_eval, m=1., k=1., ini_cndtn=[0., 1.],
                           method='RK45', user_name=None)