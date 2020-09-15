import numpy as np
import matplotlib.pyplot as plt

from simulation import HarmonicOsc1D


t_span = (0, 2 * np.pi)
n_steps = 100
t_eval = np.linspace(t_span[0], t_span[-1], 100)

simulation = HarmonicOsc1D(t_span, t_eval, m=1., k=1., ini_cndtn=[0., 1.],
                           method='RK45', user_name=None)

solution = simulation.simulate()

print("time = ", solution.t)
print("y = ", solution.y)

plt.figure()
plt.plot(solution.y[0], solution.y[1])
plt.xlabel('q')
plt.ylabel('p')
plt.title('Phase space')
plt.show()
plt.close()

plt.figure()
plt.plot(solution.t, solution.y[0], label='q(t)')
plt.plot(solution.t, solution.y[1], label='p(t)')
plt.xlabel('t')
plt.ylabel('Canonical coordinate')
plt.title('Solution')
plt.legend
plt.show()
plt.close()