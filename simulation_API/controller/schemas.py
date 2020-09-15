

from enum import Enum

from pydantic import BaseModel

# System being simulated, this is used in main.py to create predefined paths
class Sim_system(str, Enum):
    """This is a list of the available systems to simulate"""
    ho = "Harmonic-Oscillator"
    qho = "Quantum-Harmonic-Oscillator" #Just an example. Not simulating it.

class Harmonic_Oscillator(BaseModel):
    # Write base model for harmonic oscillator
    pass
