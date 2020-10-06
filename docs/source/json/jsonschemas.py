"""This file helps us generate the JSON schemas of the pydantic models defined
in ``/simulation_API/controller/schemas.py``.

Just import the relevant pydantic model eg::

    from simulation_API.controller.schemas import SimStatus

and use::

    SimStatus.schema_json(indent=2)

as you want (print, save into a file, etc.)

Warning
-------
Be careful not to overwrite the already generated schemas as they have been
slightly modified for documentation purposes.
"""
import sys
import os

this_directory = os.path.dirname(__file__)
sys.path.append(os.path.join(this_directory, '..', '..', '..'))

from simulation_API.controller.schemas import SimStatus

file_name = os.path.join(this_directory, 'SimStatus.json')
with open(file_name, 'w') as file:
    file.write(SimStatus.schema_json(indent=2))