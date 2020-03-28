from .base import Base, engine

import os
try:
    os.remove('test_v2.db')
except Exception as e:
    print(e)

# run before __main__ if database has not been created yet
Base.metadata.create_all(engine)