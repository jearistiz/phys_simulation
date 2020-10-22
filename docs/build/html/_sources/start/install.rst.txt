.. _start-install:

===============================
Install and run PHYS Simulation
===============================

1. Before installing PHYS Simulation make sure you `install pipenv`_.

2. To download PHYS Simulation clone it from the github repository using the
   following command

   .. code-block:: bash
      
      $ git clone https://github.com/jearistiz/phys_simulation

3. Change to the directory where PHYS Simulation is installed

   .. code-block:: bash
      
      $ cd phys_simulation

4. Create a virtual environment and install all the requirements using
   ``pipenv`` (this can take several minutes)

   .. code-block:: bash
      
      $ pipenv install

5. Activate the virtual environment

   .. code-block:: bash
      
      $ pipenv shell


6. Finally, run the web application in your localhost http://0.0.0.0:5700/

   .. code-block:: bash
      
      $ pipenv run simulation_api

   You can manage ``HOST`` and ``PORT`` variables in the server configuration
   file ``~/phys_simulation/config.py``.


.. note::

   -  The project runs on a Uvicorn server. The file in charge of setting up and
      starting the server is ``~/phys_simulation/run.py``. Change the options to
      your prefferred ones.

   -  If you run the server locally you can try the frontend and API in the host
      and port you chose. The frontend is almost self-explanatory.
      
   -  If you want to try out the API, go to the :ref:`Examples <start-examples>`
      section. We also explain how to use the API in general terms in the
      :ref:`Overview <start-overview>` section.

   -  **The API has its own client documentation**, thanks to FastAPI's
      integration with Swagger (formerly OpenAPI). To read this docs, after
      starting the server go to the resource ``localhos:5700/docs`` or
      ``localhos:5700/redoc`` and refer to the documentation of the resources
      starting with  ``/api/``.

   -  If you want to stop the server, go to the terminal where you started it and
      use the shortcut ``Ctrl + C``.

   -  If you want to remove the virtual environment after using the app move to
      ``~/phys_simulation/`` directory and execute

      .. code-block:: bash

         $ pipenv --rm

.. _install pipenv: https://pypi.org/project/pipenv/
