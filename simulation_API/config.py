"""Configuration file
"""
import os

this_dir = os.path.dirname(__file__)

PATH_PLOTS = os.path.join(this_dir, 'model', 'db', 'sim_results', 'plots/')
PATH_PICKLES = os.path.join(this_dir, 'model', 'db', 'sim_results', 'pickles/')
PATH_DB = os.path.join(this_dir, 'model', 'db', 'simulations.db')
