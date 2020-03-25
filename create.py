from base import Base, Session, engine
from tables import Network, Station, Channel

import os
try:
    os.remove('test.db')
except Exception as e:
    print(e)

# run before __main__ if database has not been created yet
Base.metadata.create_all(engine)