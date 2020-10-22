# PHYS Simulation

**Github repository:** <https://github.com/jearistiz/phys_simulation>

**Documentation:** <https://phys-simulation.readthedocs.io>

**Video:** <https://www.youtube.com/watch?v=2QGRTdbjzLU>

PHYS Simulation is a web application and API built on top of
[FastAPI](https://github.com/tiangolo/fastapi).
Using PHYS Simulation you can request simulations of some physical or
mathematical systems such as the Harmonic Oscillator or the Chen-Lee Attractor
–and soon many others, stay tuned!

## More About This Project

All the information about the project, including the source code documentation is
included in the [documentation website](https://phys-simulation.readthedocs.io/).

For specific topics visit:

* **GETTING STARTED**
  * [Overview](https://phys-simulation.readthedocs.io/en/latest/start/overview.html)
  * [Examples](https://phys-simulation.readthedocs.io/en/latest/start/examples.html)
* **THE CODE**
  * [simulation_api Package](https://phys-simulation.readthedocs.io/en/latest/code_docs/simulation_api.html)
  * [Add a new simulation](https://phys-simulation.readthedocs.io/en/latest/code_docs/new_simulation.html)

## Install and run PHYS Simulation

1. Before installing PHYS Simulation make sure you
  [install pipenv](https://pypi.org/project/pipenv/).

2. To download PHYS Simulation clone it from the github repository using the
  following command

    ```bash
    $ git clone https://github.com/jearistiz/phys_simulation
    ```

3. Change to the directory where PHYS Simulation is installed

    ```bash
    $ cd phys_simulation
    ```

4. Create a virtual environment and install all the requirements using
  ``pipenv`` (this can take several minutes)

    ```bash
    $ pipenv install
    ```

5. Activate the virtual environment

    ```bash
    $ pipenv shell
    ```

6. Finally run the web application in your localhost <http://0.0.0.0:5700/>

    ```bash
    $ pipenv run simulation_api
    ```

    You can manage ``HOST`` and ``PORT`` variables in the server configuration
    file ``~/phys_simulation/config.py``.

### Notes

> - The project runs on a Uvicorn server. The file in charge of setting up and
>   starting the server is ``~/phys_simulation/run.py``. Change the options to
>   your prefferred ones.
>
> - If you run the server locally you can try the frontend and API in the host
>   and port you chose. The frontend is almost self-explanatory
>
> - If you want to try out the API, go to the
>   [Examples](https://phys-simulation.readthedocs.io/en/latest/start/examples.html)
>   section in the [official documentation](https://phys-simulation.readthedocs.io/).
>   We also explain how to use the API in general terms in the
>   [Overview](https://phys-simulation.readthedocs.io/en/latest/start/overview.html)
>   section.
>
> - **The API has its own client documentation**, thanks to FastAPI's
>   integration with Swagger (formerly OpenAPI). To read this docs, after
>   starting the server go to the resource ``localhos:5700/docs`` or
>   ``localhos:5700/redoc`` and refer to the documentation of the resources
>   starting with  ``/api/``.
>
> - If you want to stop the server, go to the terminal where you started it and
>   use the shortcut ``Ctrl + C``.
>
> - If you want to remove the virtual environment after using the app move to
>   ``~/phys_simulation/`` directory and execute
>
>   ```bash
>       $ pipenv --rm
>   ```

## Frameworks and Concepts

Some of the concepts and frameworks needed to develop this application are
listed below:

* HTTP: Hypertext Transfer Protocol
* FastAPI: Python framework used to develop APIs
* SQL: Sequel Query Language
* SQLAlchemy: Python library for database management
* Pytests: Python unitary tests
* HTML: Hypertext Markup Language
* CSS: Cascade Style Sheet
* Jinja: HTML templates framework
* Sphinx: Python documentation framework
