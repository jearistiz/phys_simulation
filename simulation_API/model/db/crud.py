"""This program manages database querys.
CRUD comes from: Create, Read, Update, and Delete.
"""
from sqlalchemy.orm import Session

from .models import *
from simulation_API.controller.schemas import *


def _create_user(db: Session, user: UserDBSchCreate) -> UserDB:
    """Inserts user in users table"""
    # Create a user instance from database models
    db_user = UserDB(**user.dict())
    # Add db_user to session
    db.add(db_user)
    # Commit user to database (write data in disk)
    db.commit()
    # Refresh db_user (this will refresh the user with other information
    # contained in db e.g. automatically generated ids) 
    db.refresh(db_user)
    # Finally return the user that was geretated 
    return db_user

def _create_simulation(db: Session,
                       simulation: SimulationDBSchCreate) -> SimulationDB:
    """Inserts simulation in simulations table"""
    db_simulation = SimulationDB(**simulation.dict())
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


def _get_simulation(db: Session, sim_id: str) -> SimulationDB:
    """Get simulation from simulations table"""
    return db.query(SimulationDB).filter(SimulationDB.sim_id == sim_id).first()


def _create_plot_query_values(db: Session,
                             plot_query_params: List[PlotDBSchCreate]) -> None:
    """Insert row in plots table (contains plot query params)"""
    db_plot_query_params = [
        PlotDB(**plot_qp.dict()) for plot_qp in plot_query_params
    ]
    db.bulk_save_objects(db_plot_query_params)
    db.commit()
    return 


def _get_plot_query_values(db: Session, sim_id: str):
    """Return plot query parameters for a given simulation"""
    return [
        result[-1] for result in 
        db.query(PlotDB.plot_query_value).filter(PlotDB.sim_id == sim_id).all()
    ]
