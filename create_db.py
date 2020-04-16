from orm.base import Base, engine
from orm.tables import *

# using sqlalchemy 
Base.metadata.create_all(engine)