import numpy as np

from simulation import HarmonicOsc1D


t_span = (0, 3)
n_steps = 100
t_eval = np.linspace(t_span[0], t_span[-1], 100)

simulation = HarmonicOsc1D(t_span, t_eval, m=1., k=1., ini_cndtn=[0., 1.],
                           method='RK45', user_name=None)

solution = simulation.simulate()

print("time = ", solution.t)
print("y = ", solution.y)