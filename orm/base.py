from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_config import DB_Config

db_config = DB_Config()

engine = create_engine(db_config.get_url_conn_str_form('postgres_rds'))

Base = declarative_base()
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine, autoflush=False)
