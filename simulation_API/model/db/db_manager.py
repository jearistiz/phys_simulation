"""This module handles all the database interactions with our API"""
from sqlalchemy import create_engine, Column, Integer, String
# declarative_base is needed to create tables and add entries to tables
from sqlalchemy.ext.declarative import declarative_base
"""sessionmaker is needed to use all the Object Relational Mapper (ORM)
capabilities of sqlalchemy to read more about ORM visit 
https://docs.sqlalchemy.org/en/13/orm/tutorial.html or read the references
in Personal CS Projects notebook"""
from sqlalchemy.orm import sessionmaker


from simulation_API.config import PATH_DB

# Start sqlalchemy engine.
# Set echo=True to see queries called by sqlalchemy. Set to false in production!
engine = create_engine('sqlite:///' + PATH_DB, echo=True)
# We can execute queries directly on engine by running
# engine.execute("<<SQL Query>>") or by creating a connection (other method).
# However, the ORM method is very powerful and more "pythonic". ORM is the
# style of code we will use here.


# To use ORM we need to start a session by instantiating sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Base is an instance of declarative_base needed to use ORM
Base = declarative_base()

# Create a class (inheriting Base) representting a table:
class UserDB(Base):
    # __tablename__ attribute is mandatory and will be the name of the table
    __tablename__ = 'users'

    # It is mandatory: one of the columns be a primary key
    # unique=True indicates username should be unique
    user_id = Column(Integer(), primary_key=True, unique=True)

    # Nullable parameter set to false indicates username can NOT be empty
    # TODO In the future username MUST be UNIQUE (loggin purposes)
    username = Column(String(20), nullable=False)

    # We will follow FastAPI security recommendations which use 60 char hashes
    hash_value = Column(String(60))

    # This will represent the instances of self (User) when printed
    def __repr__(self):
        return f"User(user_id='{self.user_id}', " \
                      f"username='{self.username}', " \
                      f"hash_value='{self.hash_value}')"

"""
class SimulationDB(Base):
    __tablename__ = 'simulations'
"""

###########################################################################
# This method creates all the tables we defined. We need to call it AFTER #
#                          defining the tables                            #
Base.metadata.create_all(engine)
###########################################################################

# To insert data in our db we need to follow 3 steps (there are other methods):
# 1) Instantiate the class representing the table we want to add info to
user = UserDB(username='jose')
# 2) Add the previous instance to the session via add() method
session.add(user)
# 3) Commit the querry to our database via commit() method;
#    this will change the database in disk and effectively add user to it.
session.commit()