"""This program creates all the models and tables in the database"""
from sqlalchemy import (Column, Integer, String, Boolean, Float, ForeignKey)
from sqlalchemy.orm import relationship

from .db_manager import Base


# Create a class (inheriting Base) representting a table:
class UserDB(Base):
    """Users table model.
    
    This table stores basic user information.
    
    \f
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
    """Hash value of the usser's password."""

    # Relationships to understand them see
    # https://docs.sqlalchemy.org/en/13/orm/backref.html 
    simulations = relationship("SimulationDB", back_populates="user")
    """ORM relationship with simulations' table."""


    # This will represent the instances of self (User) when printed
    def __repr__(self):
        return f"UserDB(user_id='{self.user_id}', " \
                      f"username='{self.username}', " \
                      f"hash_value='{self.hash_value}')"


class SimulationDB(Base):
    """Simulation Status table model."""
    __tablename__ = "simulations"

    # Columns
    sim_id = Column(String(32), primary_key=True, nullable=False)
    """Simulation ID."""
    # Note here we define a relationship bweteen
    # users.user_id and simulations.user_id via the ForeignKey() argument
    user_id = Column(Integer(), ForeignKey("users.user_id"), nullable=False) 
    """Foreign key: :attr:`~.models.UserDB.user_id`."""
    date = Column(String(26), nullable=False)
    """ """
    system = Column(String(100), nullable=False)
    """Simulated system."""
    method = Column(String(10))
    """Integration method."""
    route_pickle = Column(String(52))
    """API route to GET simulation results in pickle format."""
    route_results = Column(String(150))
    """API route to GET simulation results displayed in frontend web page."""
    route_plots = Column(String(50))
    """API route to GET simulation plots."""
    success = Column(Boolean(), nullable=False)
    """Tells if the simulation was successful or not."""
    message = Column(String(500))
    """Message with further information about the simulation status."""

    # Relationships
    user = relationship("UserDB", back_populates="simulations")
    """ORM relationship with users' table."""
    plots = relationship("PlotDB", back_populates="simulation")
    """ORM relationship with plots' table."""
    parameters = relationship("ParameterDB", back_populates="simulation")
    """ORM relationship with parameters' table."""

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
    """
    __tablename__ = "plots"

    # Columns
    plot_id = Column(Integer(), primary_key=True)
    """Primary key."""
    sim_id = Column(String(32), ForeignKey("simulations.sim_id"), nullable=False)
    """Simulation ID."""
    plot_query_value = Column(String(20), nullable=False)
    """Label of each plot, used as query value for query param ``value`` in
    route ``/api/results/{sim_id}/plot``.
    """

    # Relationships
    simulation = relationship("SimulationDB", back_populates="plots")
    """ORM relationship with simulations' table."""

    def __repr__(self):
        return f"PlotDB(plot_id={self.plot_id}, " \
                        f"sim_id={self.sim_id}, " \
                        f"plot_query_value={self.plot_query_value})"


class ParameterDB(Base):
    """Parmaeters table model.
    
    Stores parameters and initial conditions of simulations.
    """
    __tablename__ = "parameters"

    param_id = Column(Integer(), primary_key=True)
    sim_id = Column(String(32), ForeignKey("simulations.sim_id"), nullable=False)
    """Simulation ID."""
    # values will be "parameter" or "initial condition"
    param_type = Column(String(17), nullable=False)
    """Parameter type, wether ``'initial condition'`` or ``'parameter'``."""
    # if param_type = "parameter" param_key is the name of the parameter
    param_key = Column(String(5))
    """Name of parameter. Must be one of the required parameters related to
    the system being simulated."""
    # if param_type = "initial condition" then init_cndtn_id is position in the array
    ini_cndtn_id = Column(Integer())
    """Initial condition position in array of initial conditions."""
    # this is the value of the parameter wether it be "initial condition" or "parameter"
    value = Column(Float, nullable=False)
    """Value of ``'parameter'`` or ``initial contidion``."""
    
    # Relationships
    simulation = relationship("SimulationDB", back_populates="parameters")
    """ORM relationship with simulations' table."""

    def __repr__(self):
        return f"ParameterDB(param_id={self.param_id}, " \
                             f"sim_id={self.sim_id}, " \
                             f"param_type={self.param_type}, " \
                             f"param_key={self.param_key}, " \
                             f"init_cndtn_id={self.init_cndtn_id}, " \
                             f"value={self.param_value})"