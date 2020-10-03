"""This module starts the database engine, the database session and the
basemodel for the database tables."""
from sqlalchemy import create_engine
# declarative_base is needed to create tables and add entries to tables
from sqlalchemy.ext.declarative import declarative_base
# sessionmaker is needed to use all the Object Relational Mapper (ORM)
# capabilities of sqlalchemy to read more about ORM visit 
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html or read the references
# in Personal CS Projects notebook
from sqlalchemy.orm import sessionmaker

from simulation_API.config import PATH_DB

# Start sqlalchemy engine.
# Set echo=True to see queries called by sqlalchemy. Set to false in production!
# From FastAPI docs, connect_args={"check_same_thread": False} is needed for
# SQLite # TODO TODO TODO Read more about it 
simulations_db_URL = 'sqlite:///' + PATH_DB
engine = create_engine(simulations_db_URL,
                       connect_args={"check_same_thread": False},
                       echo=True)
# We can execute queries directly on engine by running
# engine.execute("<<SQL Query>>") or by creating a connection (other method).
# However, the ORM method is very powerful and more "pythonic". ORM is the
# style of code we will use here. ORM = Object Relational Mapper

# To use ORM we need to create a session class by instantiating sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is an instance of declarative_base needed to use ORM
# This will help us define the tables in models.py
Base = declarative_base()