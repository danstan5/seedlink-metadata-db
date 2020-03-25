from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('postgresql://dan:pass@localhost:5432/sqlalchemy')
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine, autoflush=False)
