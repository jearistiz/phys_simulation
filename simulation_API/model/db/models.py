"""This program creates all the models and tables in the database"""
from sqlalchemy import (Column, Integer, String, Boolean, Float, ForeignKey)
from sqlalchemy.orm import relationship

from .db_manager import Base


# Create a class (inheriting Base) representting a table:
class UserDB(Base):
    """Users"""
    # __tablename__ attribute is mandatory and will be the name of the table
    __tablename__ = "users"


    #Columns

    # It is mandatory: one of the columns be a primary key
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
    """Simulation Status"""
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
    """Stores query parameter values of plots needed to access simulation
    results via GET in route /api/results/{sim_id}/plot?value={plot_query_value}
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
    """Stores parameters and initial conditions of simulations"""
    __tablename__ = "parameters"

    param_id = Column(Integer(), primary_key=True)
    sim_id = Column(String(32), ForeignKey("simulations.sim_id"), nullable=False)
    # values will be "parameter" or "init_cond_i" where i is the position of
    # initial condition in array
    param_type = Column(String(11), nullable=False)
    param_value = Column(Float, nullable=False)
    # Relationships
    simulation = relationship("SimulationDB", back_populates="parameters")

    def __repr__(self):
        return f"ParameterDB(param_id={self.param_id}, " \
                             f"sim_id={self.sim_id}, " \
                             f"param_type={self.param_type}, " \
                             f"param_value={self.param_value})"