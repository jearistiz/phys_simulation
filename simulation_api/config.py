"""General configurations of our API.
"""
import os

# Path of this directory
this_dir = os.path.dirname(__file__)

# Path of database
PATH_DB = os.path.join(this_dir, 'model', 'db', 'simulations.db')

# Path of directory of generated pickles
PATH_PICKLES = os.path.join(this_dir, 'model', 'db', 'sim_results', 'pickles/')

# Path of directory of generated plots
PATH_PLOTS = os.path.join(this_dir, 'model', 'db', 'sim_results', 'plots/')

# Image format of plots
PLOTS_FORMAT = ".png"
