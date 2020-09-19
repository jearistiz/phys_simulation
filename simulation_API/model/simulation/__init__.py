from enum import Enum

from .simulation import *

# Update this dict with all available simulations
Simulations = {
    HarmonicOsc1D.system: HarmonicOsc1D,
    "Quantum_Harmonic_Oscillator": None
}

SimSystem = Enum(
    'SimSystem', {sys: "-".join(sys.split("_")) for sys in Simulations.keys()}
)
