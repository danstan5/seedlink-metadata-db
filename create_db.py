from db.orm.base import Base, engine
from db.orm.tables import *

# using sqlalchemy 
Base.metadata.create_all(engine)