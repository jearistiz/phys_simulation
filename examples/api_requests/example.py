"""This is an example of the workflow of the 
"""
import sys
import os
from time import sleep

import requests

this_directory = os.path.dirname(__file__)
sys.path.append(os.path.join(this_directory, '..', '..', '..'))

from simulation_fastapi import config

######################### Simulation Request Example ##########################

# Prepare the simulation request
sim_system = "Chen-Lee-Attractor"
sim_request = {
    "system": sim_system,
    "username": "PHYSSimulation",
    "t_span": [0, 200],
    "t_steps": 1e5,
    "ini_cndtn": [10, 10, 0],
    "params": {
        "a": 3,
        "b": -5,
        "c": -1,
    }
}

# PHYS Simulation index URI
url = 'http://' + config.HOST + ':' + str(config.PORT)

# Simulation request route
sim_requrest_route = f'/api/simulate/{sim_system}'

# Request simulation via HTTP using `requests` module
sim_request_response = requests.post(url + sim_requrest_route, json=sim_request)

# Print response
print(
    "",
    "Simulation Request Response",
    "----------------------------------------",
    f"HTML status code: {sim_request_response.status_code}",
    "Response:",
    "    {",
    sep='\n',
)
for key, v in sim_request_response.json().items():
    print(f"        '{key}': {v},")
print("    }")



########################## Simulation Status Example ##########################

# Wait until the simulation is done
sleep(5)

# Get simulation ID
sim_id = sim_request_response.json()["sim_id"]

# Simulation status route
sim_status_route = f"/api/simulate/status/{sim_id}"

# Request simulation status via HTTP using `requests` module
sim_status_response = requests.get(url + sim_status_route)

# Print response
sim_status_response_json = sim_status_response.json()
print(
    "",
    "Simulation status Response",
    "----------------------------------------",
    f"HTML status code: {sim_status_response.status_code}",
    "Response:",
    "    {",
    sep='\n',
)
for key, v in sim_status_response_json.items():
    print(f"        '{key}': {v},")
print("    }\n")


############################# GET Results Example #############################

if not sim_status_response_json["success"]:
    print("Warning: pickle and plot files not available.\n")
    sys.exit(1)

# Pickle download route
pickle_route = sim_status_response.json()["route_pickle"]

# Request simulation status via HTTP using `requests` module
pickle_response = requests.get(url + pickle_route, stream=True)

# Save Pickle
with open(this_directory + '/simulation.pickle', 'wb') as file:
    file.write(pickle_response.content)

# Plots download route
plots_route = sim_status_response.json()["route_plots"]

# Plot query values
plot_query_values = sim_status_response.json()["plot_query_values"]

for qv in plot_query_values:
    # Construct the URI query for each plot
    plot_query_url = url + plots_route + "?value=" + qv

    # Request the plot
    plot_response = requests.get(plot_query_url, stream=True)

    # Save the plot in a file
    plot_file_name = this_directory + "/plot_" + qv + ".png"
    with open(plot_file_name, 'wb') as file:
        file.write(plot_response.content)
