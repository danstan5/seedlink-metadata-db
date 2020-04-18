from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.config import Config

config = Config()

engine = create_engine(config.get_conn_str())

Base = declarative_base()
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine, autoflush=False)
