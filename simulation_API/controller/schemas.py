"""This module defines all the models/schemas needed in our application, except
the database models required for sqlalchemy ORM.
"""
from typing import Optional, List, Dict, Union
from enum import Enum
from datetime import datetime

from pydantic import BaseModel
from scipy.integrate._ivp.ivp import OdeResult
from numpy import pi

"""How to add a new system to this API?

    1)  Add Simulation in simulations module and test it. 
    2)  Add the relevant simulation to Simulations dict located in __init__
        in simulations module.
    3)  Add relevant schemas and models to schemas.py
    4)  Add relevant form entries in frontend.
    4)  Add relevant plots to _plot_solution in tasks.py –do not forget to add.
        plot_query_value for each plot.
    5)  Add frontend results HTML template to show plots.
"""


###############################################################################
################### Schemas needed in main.py and tasks.py ####################
###############################################################################

###################### Available systems for simulation #######################

# NOTE: Needs update each time a new simulation is added
class SimSystem(str, Enum):
    """List of available systems for simulation.
    
    \f
    Attributes
    ----------
    HO : str
        Harmonic Oscillator Enum attribute.
    ChenLee : str
         Chen-Lee Attractor Enum attribute.

    Warning
    -------
    The values of the attributes of this class must coincide with the
    dictionary keys defined in
    :data:`simulation_API.simulation.simulations.Simulations`, otherwise the
    system won't be simulated by the backend.

    Warning
    -------
    This class needs update each time a new simulation is added: add an
    appropiate new attribute.
    """
    HO = "Harmonic-Oscillator"
    ChenLee = "Chen-Lee-Attractor"



######################## Available Integration Methods ########################

# Enum needed to verify correct values with API
# NOTE: Update this with relevant parameters
class IntegrationMethods(str, Enum):
    """List of available integration methods
    
    \f
    Attributes
    ----------
    RK45 : str
        Explicit Runge-Kutta method of order 5(4).
    RK23 : str
        Explicit Runge-Kutta method of order 3(2).
    
    Note
    ----
    For more information about these integration methods see
    `scipy.integrate.solve_ivp <https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html>`_.
    
    Warning
    -------
    This class needs update each time a new simulation is added: add an
    appropiate new attribute.
    """
    RK45 = "RK45"
    RK23 = "RK23"


# Needed to generate dict used to display available integration methods in frontend
# NOTE: Needs update each time a new simulation is added. Needs to coincide
# with Integration Methods
class IntegrationMethodsFrontend(str, Enum):
    """List of captions of available integration methods. These are displayed
    in frontend simulation form.

    Warning
    -------
    This class needs update each time a new simulation is added: add an
    appropiate new attribute.
    """
    RK45 = "Runge-Kutta 5(4)"
    RK23 = "Runge-Kutta 3(2)"

# Used in frontend and generated automatically from IntegrationMethodsFrontend
integration_methods = {
    member[0]: member[1].value
        for member in IntegrationMethodsFrontend._member_map_.items()
}



###################### Frontend Simulation Form schemas #######################

# NOTE Needs update each time a new simulation is added. 
# NOTE      1) create a new pydantic class similar to HOSimForm. 
# NOTE      2) add the class to the dict `SimFormDict` defined somewhere below.
class SimForm(BaseModel):
    """Basemodel of schema used to Request a Simulation in Frontend.
    
    Attributes
    ----------
    username: Optional[str]
    t0 : float
        Initial time of simulation.
    tf : float
        Final time of simulation.
    dt : float
        Time step size of simulation.
    method : IntegrationMethods
        Integration method used in simulation.

    Warning
    -------
    Needs update each time a new simulation is added:

    1. Create a new appropiate class similar to
       :class:`~simulation_API.controller.schemas.HOSimForm` or to
       :class:`~simulation_API.controller.schemas.ChenLeeSimForm`.
    2. Add the class to the dict :data:`~simulation_API.controller.schemas.SimFormDict`
       defined somewhere in this module.
    """
    username: Optional[str] = "Pepito"
    t0: Optional[float] = 0.0
    tf: Optional[float] = 2 * pi
    dt: Optional[float] = pi / 10
    method: Optional[IntegrationMethods] = "RK45"


class HOSimForm(SimForm):
    """Schema used to Request Harmonic Oscillator Simulation in Frontend via
    form.
    
    Attributes
    ----------
    sim_system : SimSystem
        System to be simulated.
    ini0 : float
        :math:`q` initial value.
    ini1 : float
        :math:`p` initial value.
    param0 : float
        Paramer of name :attr:`~simulation_API.controller.schemas.HOParams.m`.
    param1 : float
        Paramer of name :attr:`~simulation_API.controller.schemas.HOParams.k`.

    Note
    ----
    For more information about Chen-Lee Attactor simulation see 
    :class:`~simulation_API.simulation.simulations.HarmonicOsc1D`.
    """
    sim_sys: SimSystem = SimSystem.HO.value
    ini0: Optional[float] = 1.0
    ini1: Optional[float] = 0.0
    param0: Optional[float] = 1.0
    param1: Optional[float] = 1.0


class ChenLeeSimForm(SimForm):
    """Schema used to Request Chen Lee Simulation in Frontend via form.
    
    Attributes
    ----------
    sim_system : SimSystem
        System to be simulated.
    ini0 : float
        :math:`\omega_x` initial condition.
    ini1 : float
        :math:`\omega_y` initial condition.
    ini2 : float
        :math:`\omega_z` initial condition.
    param0 : float
        Paramer of name :attr:`~simulation_API.controller.schemas.ChenLeeParams.a`.
    param1 : float
        Paramer of name :attr:`~simulation_API.controller.schemas.ChenLeeParams.b`.
    param2 : float
        Paramer of name :attr:`~simulation_API.controller.schemas.ChenLeeParams.c`.

    Note
    ----
    For more information about Chen-Lee Attactor simulation see 
    :class:`~simulation_API.simulation.simulations.ChenLeeAttractor`.
    """
    sim_sys: SimSystem = SimSystem.ChenLee.value
    ini0: Optional[float] = 10.0
    ini1: Optional[float] = 10.0
    ini2: Optional[float] = 0.0
    param0: Optional[float] = 3.0
    param1: Optional[float] = - 5.0
    param2: Optional[float] = - 1.0



############################ Simulation Parameters ############################

# NOTE Needs update each time a new system is added (add a new class).
class HOParams(BaseModel):
    """List of parameters of the Harmonic Oscillator system.
    
    Attributes
    ----------
    m: float
        Mass of object.
    k: float
        Force constant of object.

    Note
    ----
    For more information about Harmonic Oscillator's parameters see 
    :class:`~simulation_API.simulation.simulations.HarmonicOsc1D`.

    Warning
    -------
    This needs update each time a new simulation is added: add an
    appropiate new class similar to this one or to
    :class:`simulation_API.controller.schemas.ChenLeeParams`.
    """
    m: float    # Mass
    k: float    # Force constant


class ChenLeeParams(BaseModel):
    """List of parameters of the Chen-Lee Attractor system.

    Attributes
    ----------
    a : float
        :math:`\omega_x` parameter.
    b : float
        :math:`\omega_y` parameter.
    c : float
        :math:`\omega_z` parameter.

    Note
    ----
    For more information about Chen-Lee Attactor's parameters see 
    :class:`~simulation_API.simulation.simulations.ChenLeeAttractor`.

    Warning
    -------
    This needs update each time a new simulation is added: add an
    appropiate new class similar to this one or to
    :class:`simulation_API.controller.schemas.HOParams`.
    """
    a: float
    b: float
    c: float


# Maps each system to its parameters (used in backend)
# NOTE Needs update each time a new system is added
SimSystem_to_SimParams = {
    SimSystem.HO.value: HOParams,
    SimSystem.ChenLee.value: ChenLeeParams,
}
"""Maps the name of each available system to its parameters model

Warning
-------
Needs update each time a new simulation is added: add a new appropiate item
to this dict.
"""


# Maps systems to pydantic schemas used in route "/simulate/{sim_system}"
# NOTE Needs update each time a new system is added (add new entry in dict).
SimFormDict = {
    SimSystem.HO.value: HOSimForm,
    SimSystem.ChenLee.value: ChenLeeSimForm
}
"""Maps the name of each available system to its simulation form model.

Warning
-------
Needs update each time a new simulation is added: add a new appropiate item
to this dict.
"""

# This dicts map different conventions for simulation parameter names 
# {param_name_frontend: param_name_backend}
# NOTE Needs update each time a new system is added (add new dict with params).
params_mapping_HO = {
    "param0": "m",
    "param1": "k",
}
"""Maps the name of each Harmonic Oscillator parameter in frontend form to its
name in backend (defined by its corresponding attribute in class
:class:`~simulation_API.simulation.simulations.HarmonicOsc1D`)
"""
params_mapping_ChenLee = {
    "param0": "a",
    "param1": "b",
    "param2": "c",
}
"""Maps the name of each Chen-Lee Attractor parameter in frontend form to its
name in backend (defined by its corresponding attribute in class
:class:`~simulation_API.simulation.simulations.ChenLeeAttractor`)
"""

# This dict maps each system to its parameter change-of-convention
# dictionary defined above (used in frontend simulation request)
system_to_params_dict = {
    SimSystem.HO.value: params_mapping_HO,
    SimSystem.ChenLee.value: params_mapping_ChenLee,
}
"""Maps the name of each available system to its parameter change-of-convention
mapping (e.g. :data:`~simulation_API.controller.schemas.params_mapping_HO` or
:data:`~simulation_API.controller.schemas.params_mapping_ChenLee`.) 

This is used to translate the parameters name convention in frontend simulation
request to the parameters name convention in backend simulation request (with
appropiate schema given by
:class:`simulation_API.controller.schemas.SimRequest`.)
"""



########################## Simulation Request schema ##########################

class SimRequest(BaseModel):
    """Schema needed to request simulations via POST in
    ``/api/request/{sim_system}``.
    
    For the attributes that do not have a description see
    :class:`simulation_API.simulation.simulations.Simulation`.

    Note
    ----
    Most of the attributes in this pydantic class are arguments of the 
    classes defined in the module :mod:`simulation_API.simulation.simulations`,
    for more information please refer to It.

    Attributes
    ----------
    system : SimSystem
    t_span : List[float]
    t_eval : List
    t_steps : int
    ini_cndtn : List[float]
    params : Dict[str, float]
    method : IntegrationMethods
    sim_id : str
        ID of simulation. This is handled internally, leave it blank
        when requesting a simulation.
    user_id : int
        User id number stored in database. This is handled internally, leave it
        blank when requesting a simulation.
    username : str
    """
    system: SimSystem = SimSystem.HO
    t_span: List[float] = []
    t_eval: Optional[List[float]] = []
    t_steps: Optional[int] = 0
    ini_cndtn: List[float] = []
    params: Dict[str, float]
    method: Optional[IntegrationMethods] = 'RK45'
    # The backend will assign a sim_id, so it is not necessary to provide one.
    sim_id: Optional[str] = None
    # If we implement logging, user_id will be handled by backend
    user_id: Optional[int] = 0
    username: str = "Pepito Perez"



### Simulation ID response schema when simulation is requested in frontend. ###

class SimIdResponse(BaseModel):
    """Schema for the response of a simulation request (requested via POST in
    route ``/api/simulate/{sim_sys}``.)

    Note
    ----
    The request of the simulation must follow the model
    :class:`~simulation_API.controller.schemas.SimRequest`.

    Attributes
    ----------
    sim_id : str
        ID of simulation.
    user_id : int
        User id number stored in database.
    username : str
    sim_sys : SimSystem
        Simulated system.
    sim_status_path : str
        Path to GET the status of the simulation.
    sim_pickle_path : str
        Path to GET (download) a pickle with the results of the simulation.
    message : str
        Explanatory message.
    """
    sim_id: Optional[str]
    user_id: Optional[int]
    username: Optional[str]
    sim_sys: Optional[SimSystem]
    sim_status_path: Optional[str]
    sim_pickle_path: Optional[str]
    message: Optional[str]



###### Plot Query values needed to download the plots of each simulation ######

# NOTE Needs update each time a new system is added (add a new class).
class PlotQueryValues_HO(str, Enum):
    """List of tags of each different plot generated automatically by the
    backend when a Harmonic Oscillator simulation is requested.
    
    These tags are used as the possible values of the querry param ``value``
    in route ``/api/results/{sim_id}/plot?value=<plot_query_value>``.

    Note
    ----
    :attr:`simualtion_API.controller.shcemas.SimIdResponse.sim_id` must be
    related to the Harmonic Oscillator system.
    """
    coord = "coord"
    phase = "phase"


class PlotQueryValues_ChenLee(str, Enum):
    """List of tags of each different plot generated automatically by the
    backend when a Chen-Lee simulation is requested.
    
    These tags are used as the possible values of the querry param ``value``
    in route ``/api/results/{sim_id}/plot?value=<plot_query_value>``.
    
    Note
    ----
    :attr:`simualtion_API.controller.schemas.SimIdResponse.sim_id` must be
    related to the Chen Lee system.
    """
    threeD = "threeD"
    project = "project"


# NOTE Needs update each time a new system is added (new entry w/ name of new class)
PlotQueryValues = Union[
    PlotQueryValues_HO,
    PlotQueryValues_ChenLee,
]
"""Union of the classes defining Enums of plot query values for each system.
This is needed in :class:`~simualtion_API.controller.schemas.SimStatus`."""



######################### Simulation Results Schemas ##########################

class SimResults(BaseModel):
    """Results of simulation as returned by ``scipy.integrate.solve_ivp``"""
    sim_results: OdeResult



########################### Simulation Status Schema ##########################

class SimStatus(BaseModel):
    """Schema of the status of simulations.

    This pydantic model is intended to store paths of results of the
    simulations algong with some metadata. This information can be accessed via
    GET in ``/api/simulate/status/{sim_id}``.
    
    Attributes
    ---------
    sim_id : int
        ID of simulation.
    user_id : int
        User id number stored in database.
    date : datetime
        Date of request of simulation.
    system : SimSystem
        Simulated system.
    route_pickle : str
        Route of pickle file generated by the simulation.
    route_results : str
        Route of frontend showing results.
    route_plot : list
        Route of plots generated by the simulation backend.
    plot_query_values : List[str]
        Query params values of different automatically generated plots.
        These values are needed to download the plots in route 
        ``/api/results/{sim_id}/plot?value=<plot_query_value>``.
    success : bool
        Success status of simulation.
    message : str
        Additional information on status of simulation.
    """
    # User-related attributes
    sim_id: str
    user_id : int
    date: datetime

    # Simulation-related attributes
    system: Optional[SimSystem]
    ini_cndtn: Optional[List[float]]
    params: Optional[Dict[str, float]]
    method: Optional[IntegrationMethods]

    # Response-related attributes
    route_pickle: Optional[str]
    route_results: Optional[str]
    route_plots: Optional[str]
    plot_query_values: Optional[List[PlotQueryValues]]
    plot_query_receipe: Optional[str] = \
        "'route_plots' + '?value=' + 'plot_query_value'"
    success : Optional[bool]
    message : Optional[str]




###############################################################################
################### Schemas needed for databse interaction ####################
###############################################################################

############################ Users ############################
class UserDBSchBase(BaseModel):
    """Basemodel for API type checking when querrying ``users`` table in
    ``simulations.db`` database.
    """
    username: Optional[str]


class UserDBSch(UserDBSchBase):
    """Model for API type checking when reading a user information in
    ``users`` table in ``simulations.db`` database.
    """
    user_id : Optional[int]
    class Config:
        """This class is needed for database reading optimization
        (thanks to Object Relational Mapper –ORM.)
        
        Note
        ----
        Read more in
        `FastAPI docs <https://fastapi.tiangolo.com/tutorial/sql-databases/#use-pydantics-orm_mode>`_.
        """
        orm_model = True


class UserDBSchCreate(BaseModel):
    """Model for API type checking when creating a 'user information' row
    in ``users`` table in ``simulations.db`` database.
    """
    # Just for now store Null hash TODO TODO TODO change when logging
    # Production username and hash_value must be mandatory
    username : str
    hash_value: Optional[str]
    pass


############################ Simulation status ############################
class SimulationDBSchBase(BaseModel):
    """Basemodel for API type checking when querrying ``simulations`` table in
    ``simulations.db`` database.
    """
    sim_id: Optional[str]
    user_id: Optional[int]
    date: Optional[str]
    system: Optional[str]
    method: Optional[str]
    route_pickle: Optional[str]
    route_results: Optional[str]
    route_plots: Optional[str]
    success: Optional[bool]
    message: Optional[str]


class SimulationDBSch(SimulationDBSchBase):
    """Model for API type checking when reading a row in
    ``simulations`` table in ``simulations.db`` database.
    """
    class Config:
        """This class is needed for database reading optimization
        (thanks to Object Relational Mapper –ORM.)
        
        Note
        ----
        Read more in
        `FastAPI docs <https://fastapi.tiangolo.com/tutorial/sql-databases/#use-pydantics-orm_mode>`_.
        """
        orm_model = True


class SimulationDBSchCreate(SimulationDBSchBase):
    """Model for API type checking when creating a 'simulation information' row
    in ``simulations`` table in ``simulations.db`` database.
    """
    sim_id: str
    user_id: int
    date: str
    system: str
    success: bool
    

############################ Plots ############################
class PlotDBSchBase(BaseModel):
    """Basemodel for API type checking when querrying ``plots`` table in
    ``simulations.db`` database.
    """
    sim_id: Optional[str]
    plot_query_value: Optional[str]


class PlotDBSch(PlotDBSchBase):
    """Model for API type checking when reading a row in ``plots``
    table in ``simulations.db`` database.
    """
    plot_id: Optional[int]
    class Config:
        """This class is needed for database reading optimization
        (thanks to Object Relational Mapper –ORM.)
        
        Note
        ----
        Read more in
        `FastAPI docs <https://fastapi.tiangolo.com/tutorial/sql-databases/#use-pydantics-orm_mode>`_.
        """
        orm_model = True


class PlotDBSchCreate(PlotDBSchBase):
    """Model for API type checking when creating a 'plot information' row in
    ``plots`` table in ``simulations.db`` database.
    """
    sim_id: str
    plot_query_value: str


############################ Parameters ############################
class ParamType(str, Enum):
    """These are the possible values of ``param_type`` column in ``parameters``
    table in ``simulations.db`` database.
    """
    ini_cndtn = "initial condition"
    param = "parameter"


class ParameterDBSchBase(BaseModel):
    """Basemodel for API type checking when querrying ``parameters`` table in
    ``simulations.db`` database.
    """
    sim_id: Optional[str]
    param_type: Optional[ParamType]
    param_key: Optional[str]
    ini_cndtn_id: Optional[int]
    value: Optional[float]


class ParameterDBSch(ParameterDBSchBase):
    """Model for API type checking when reading a row in ``parameters`` table
    in ``simulations.db`` database.
    """
    param_id: Optional[int]
    class Config:
        """This class is needed for database reading optimization
        (thanks to Object Relational Mapper –ORM.)
        
        Note
        ----
        Read more in
        `FastAPI docs <https://fastapi.tiangolo.com/tutorial/sql-databases/#use-pydantics-orm_mode>`_.
        """
        orm_model = True


class ParameterDBSchCreate(ParameterDBSchBase):
    """Model for API type checking when creating a row in ``parameters`` table
    in ``simulations.db`` database.
    """
    sim_id: str
    param_type: ParamType
    value: float




###############################################################################
################################ Some Messages ################################
###############################################################################

na_message = "Simulation of the system you requested is not available."
sim_id_not_found_message = "The simulation ID (sim_id) you provided is not " \
                           "yet in our database. If you are sure about the " \
                           "sim_id you provided, either your simulation has " \
                           "not finished or there was an internal server " \
                           "error. Please come back latter and check."
sim_status_finished_message = "Finished. You can request via GET: download " \
                              "simulation results (pickle) in route given " \
                              "in 'route_pickle', or; download plots of " \
                              "simulation in route 'route_plots' using " \
                              "query params the ones given in " \
                              "'plot_query_values', or; see results online " \
                              "in route 'route_results'."
