import numpy as np
import matplotlib.pyplot as plt

from simulation import HarmonicOsc1D

# Number of steps for simulation
n_steps = 100

# Parameters of simulation
t_span = (0, 2 * np.pi)
t_eval = np.linspace(t_span[0], t_span[-1], 100)
m, k = 1, 1
ini_cndtn = [1., 0.]
method = 'RK45'
user_name = 'Juan'

HO_simulation = HarmonicOsc1D(t_span, t_eval, m, k, ini_cndtn, method,
                              user_name)

HO_solution = HO_simulation.simulate()


print("Method: ", HO_simulation.method)
print("Date: ", HO_simulation.date)

plt.figure()
plt.plot(HO_solution.y[0], HO_solution.y[1])
plt.xlabel('q')
plt.ylabel('p')
plt.title('Phase space')
plt.show()
plt.close()

plt.figure()
plt.plot(HO_solution.t, HO_solution.y[0], label='q(t)')
plt.plot(HO_solution.t, HO_solution.y[1], label='p(t)')
plt.xlabel('t')
plt.ylabel('Canonical coordinate')
plt.title('Solution')
plt.legend()
plt.show()
plt.close()