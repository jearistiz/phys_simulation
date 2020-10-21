"""This program manages database querys.
CRUD comes from: Create, Read, Update, and Delete.
"""
from typing import Union, Tuple

from sqlalchemy.orm import Session

from .models import *
from simulation_api.controller.schemas import *


def _create_user(db: Session, user: UserDBSchCreate) -> UserDB:
    """Inserts ``user`` in ``users`` table.
    
    Parameters
    ----------
    db : Session
        Database Session.
    user : UserDBSchCreate
        User row in database.

    Returns
    -------
    db_user : UserDB
        Updated inserted row (with :attr:`~.models.UserDB.user_id`.)
    """
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


def _get_username(db: Session, user_id: int):
    """Gets ``user`` from ``users`` table.

    Parameters
    ----------
    db : Session
        Database Session.
    user_id : int
    
    Returns
    -------
    ``sqlalchemy.orm.Query``
        Query with information about username with given ``user_id``.
    """
    return db.query(UserDB.username).filter(UserDB.user_id == user_id).first()


def _create_simulation(db: Session,
                       simulation: SimulationDBSchCreate) -> SimulationDB:
    """Inserts simulation in simulations table.

    Parameters
    ----------
    db : Session
        Database Session.
    simulation : SimulationDBSchCreate
        Simulation row in ``simulations`` table.

    Returns
    -------
    db_simulation : SimulationDB
        Updated ``simulation``'s row.
    """
    db_simulation = SimulationDB(**simulation.dict())
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


def _get_simulation(db: Session, sim_id: str) -> SimulationDB:
    """Get simulation with specific id from simulations table.

    Parameters
    ----------
    db : Session
        Database Session.
    sim_id : str
        Simulation ID.

    Returns
    -------
    ``sqlalchemy.orm.Query``
        Query with simulation information of ``sim_id``.
    """
    return db.query(SimulationDB).filter(SimulationDB.sim_id == sim_id).first()


def _get_all_simulations(db: Session) -> Tuple[SimulationDB]:
    """Get all simulation entries in ``simulations`` table.
    
    Parameters
    ----------
    db : Session
        Database Session.

    Returns
    -------
    ``sqlalchemy.orm.Query``
        Querry of all rows in ``simulations`` table.
    """
    return db.query(SimulationDB).order_by(SimulationDB.date.desc()).all()


def _create_plot_query_values(db: Session,
                              plot_query_params: List[PlotDBSchCreate]) -> None:
    """Insert row in plots table (contains plot query params)

    Parameters
    ----------
    db : Session
        Database Session.
    plot_query_params : List[PlotDBSchCreate]
        List of rows to be inserted in ``plots`` table.

    Returns
    -------
    None
    """
    db_plot_query_params = [
        PlotDB(**plot_qp.dict()) for plot_qp in plot_query_params
    ]
    db.bulk_save_objects(db_plot_query_params)
    db.commit()
    return 


def _get_plot_query_values(db: Session, sim_id: str):
    """Return plot query parameters for a given simulation.

    Parameters
    ----------
    db : Session
        Database Session.
    sim_id : str
        Simulation ID.

    Returns
    -------
    List[:data:`~simulation_api.controller.schemas.PlotQueryValues`]
        Plot query values associated to ``sim_id``.
    """
    return [
        result[-1] for result in 
        db.query(PlotDB.plot_query_value).filter(PlotDB.sim_id == sim_id).all()
    ]


def _create_parameters(db: Session,
                       parameters: List[ParameterDBSchCreate]) -> None:
    """Insert parameter entry into parameters table.
    
    Parameters
    ----------
    db : Session
        Database Session.
    parameters: List[ParameterDBSchCreate]
        Parameter row in ``parameters``' table.
    
    Returns
    -------
    None
    """
    db_parameters = [
        ParameterDB(**parameter.dict()) for parameter in parameters
    ]
    db.bulk_save_objects(db_parameters)
    db.commit()
    return

def _get_parameters(db: Session, sim_id: str,
                    param_type: ParamType) -> Union[List[float], Dict[str, float]]:
    """Get parameters from parameters table.
    
    Parameters
    ----------
    db : Session
        Database Session.
    sim_id : str
        Simulation ID.
    param_type : ParamType
        Type of parameter, wether ``'initial condition'`` or ``'parameter'``.

    Returns
    -------
    List[float] or Dict[str, float]
        ``list`` of initial conditions or ``dict`` mapping parameter names to
        parameter values.
    """
    query = db.query(ParameterDB) \
                .filter((ParameterDB.param_type == param_type) & (ParameterDB.sim_id == sim_id)) \
                    .order_by(ParameterDB.ini_cndtn_id.asc()) \
                        .all()

    if param_type == ParamType.ini_cndtn:
        return [Param.value for Param in query]
    else:
        return {Param.param_key: Param.value for Param in query}
