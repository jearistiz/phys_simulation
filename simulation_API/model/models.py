"""This program creates all the models and tables in the database"""
from sqlalchemy import (Column, Integer, String, Boolean, Float, ForeignKey)
from sqlalchemy.orm import relationship

from .db_manager import Base


# Create a class (inheriting Base) representting a table:
class UserDB(Base):
    """Users table model.
    
    This table stores basic user information.

    Attributes
    ----------
    __tablename__
    user_id : Column, int, primary_key
    username : Column, str
    hash_value : Column, str
        Hash value of the usser's password.

    Note
    ----
    :attr:`~.models.UserDB.hash_value` and this ``users`` table is not
    appropiately used yet because logging is not yet implemented in the app.
    """
    # __tablename__ attribute is mandatory and will be the name of the table
    __tablename__ = "users"


    #Columns

    # It is mandatory: one of the columns must be a primary key
    # unique=True indicates username should be unique
    user_id = Column(Integer(), primary_key=True)

    # Nullable parameter set to false indicates username can NOT be empty
    # TODO In the future username MUST be UNIQUE (loggin purposes)
    username = Column(String(20), nullable=False)

    # We will follow FastAPI security recommendations which use 60 char hashes
    hash_value = Column(String(60))

    # Relationships to understand them see
    # https://docs.sqlalchemy.org/en/13/orm/backref.html 
    simulations = relationship("SimulationDB", back_populates="user")


    # This will represent the instances of self (User) when printed
    def __repr__(self):
        return f"UserDB(user_id='{self.user_id}', " \
                      f"username='{self.username}', " \
                      f"hash_value='{self.hash_value}')"


class SimulationDB(Base):
    """Simulation Status table model.
    
    Attributes
    ----------
    __tablename__ : str
    sim_id : Column, str, primary_key
        Simulation ID.
    user_id : Column, str
        Foreign key: :attr:`~.models.UserDB.user_id`.
    date : Column, str
    system : Column, str, :class:`~simulation_API.controller.schemas.SimSystem`
        Simulated system.
    method : Column, str, :class:`~simulation_API.controller.schemas.IntegrationMethod`
    route_pickle : Column, str
        API route to GET simulation results in pickle format.
    route_results : Column, str
        API route to GET simulation results displayed in frontend web page.
    route_plots : Column, str
        API route to GET simulation plots.
    success : Column, bool
        Tells if the simulation was successful or not.
    message : Column, str
        Message with further information about the simulation status.
    user
        ORM relationship with users' table.
    plots
        ORM relationship with plots' table.
    parameters
        ORM relationship with parameters' table.
    """
    __tablename__ = "simulations"

    # Columns
    sim_id = Column(String(32), primary_key=True, nullable=False)
    # Note here we define a relationship bweteen
    # users.user_id and simulations.user_id
    user_id = Column(Integer(), ForeignKey("users.user_id"), nullable=False) 
    date = Column(String(26), nullable=False)
    system = Column(String(100), nullable=False)
    method = Column(String(10))
    route_pickle = Column(String(52))
    route_results = Column(String(150))
    route_plots = Column(String(50))
    success = Column(Boolean(), nullable=False)
    message = Column(String(500))

    # Relationships
    user = relationship("UserDB", back_populates="simulations")
    plots = relationship("PlotDB", back_populates="simulation")
    parameters = relationship("ParameterDB", back_populates="simulation")

    def __repr__(self):
        return f"SimulationDB(sim_id={self.sim_id}, " \
                              f"user_id={self.user_id}, " \
                              f"date={self.date}, " \
                              f"system={self.system}, " \
                              f"method={self.method}, " \
                              f"route_pickle={self.route_pickle}, " \
                              f"route_results={self.route_results}, " \
                              f"route_plots={self.route_plots}, " \
                              f"success={self.success}, " \
                              f"message={self.message})"
    

class PlotDB(Base):
    """Plots table model.
    
    Stores query parameter values of plots needed to access simulation
    results via GET in route
    ``/api/results/{sim_id}/plot?value={plot_query_value}``.

    Attributes
    ----------
    __tablename__ : str
    plot_id : Column, int, primary_key
    sim_id : Column, str
        Simulation ID.
    plot_query_value : Column, str
    simulation
        ORM relationship with simulations' table.
    """
    __tablename__ = "plots"

    # Columns
    plot_id = Column(Integer(), primary_key=True)
    sim_id = Column(String(32), ForeignKey("simulations.sim_id"), nullable=False)
    plot_query_value = Column(String(20), nullable=False)

    # Relationships
    simulation = relationship("SimulationDB", back_populates="plots")

    def __repr__(self):
        return f"PlotDB(plot_id={self.plot_id}, " \
                        f"sim_id={self.sim_id}, " \
                        f"plot_query_value={self.plot_query_value})"


class ParameterDB(Base):
    """Parmaeters table model.
    
    Stores parameters and initial conditions of simulations.
    
    Attributes
    ----------
    __tablename__ : str
    param_id : Column, int, primary_key
    sim_id : Column
        Simulation ID.
    param_type : Column, str, :class:`simulation_API.controller.schemas.ParamType`
        Parameter type, wether ``'initial condition'`` or ``'parameter'``.
    param_key : Column, str
        Name of parameter. Must be one of the required parameters related to
        the system being simulated.
    ini_cndtn_id : Column
        Initial condition position in array of initial conditions.
    value : Column.
        Value of ``'parameter'`` or ``initial contidion``.
    simulation
        ORM relationship with simulations' table.
    """
    __tablename__ = "parameters"

    param_id = Column(Integer(), primary_key=True)
    """:Column, int, primary_key:"""
    sim_id = Column(String(32), ForeignKey("simulations.sim_id"), nullable=False)
    # values will be "parameter" or "initial condition"
    param_type = Column(String(17), nullable=False)
    # if param_type = "parameter" param_key is the name of the parameter
    param_key = Column(String(5))
    # if param_type = "initial condition" then init_cndtn_id is position in the array
    ini_cndtn_id = Column(Integer())
    # this is the value of the parameter wether it be "initial condition" or "parameter"
    value = Column(Float, nullable=False)
    
    # Relationships
    simulation = relationship("SimulationDB", back_populates="parameters")

    def __repr__(self):
        return f"ParameterDB(param_id={self.param_id}, " \
                             f"sim_id={self.sim_id}, " \
                             f"param_type={self.param_type}, " \
                             f"param_key={self.param_key}, " \
                             f"init_cndtn_id={self.init_cndtn_id}, " \
                             f"value={self.param_value})"