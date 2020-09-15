from simulation import HarmonicOsc1D

simulation = HarmonicOsc1D(t_span, t_eval, m=1., k=1., ini_cndtn=[0., 1.],
                           method='RK45', user_name=None)