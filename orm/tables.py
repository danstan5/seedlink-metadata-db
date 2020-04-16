from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
#from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from orm.base import Base

class Network(Base):
    __tablename__ = "network"

    code = Column(String(2), primary_key=True, unique=True)
    startdate = Column(DateTime)
    description = Column(String(120)) # enough?
    n_total_stations = Column(Integer)
    
    def __init__(self, **columns):
        self.__dict__.update(columns)

    # extra fields queriable from other databases
    def get_n_active_stations(self, session, last_datetime):
        self.n_active_stations = None # session.query() # 
        if self.n_active_stations == 0:
            self.active = 0
            self.lastactive = last_datetime


class Station(Base):
    __tablename__ = "station"

    code = Column(String(8), primary_key=True, unique=True)
    network_code = Column(String(2), ForeignKey('network.code'))
    startdate = Column(DateTime)
    sitename = Column(String(60))
    elevation = Column(Float)
    longitude = Column(Float)
    latitude = Column(Float)
    n_total_channels = Column(Integer)
    
    #network = relationship("Network", backref="station")

    def __init__(self, **columns):
        self.__dict__.update(columns)
        self.code = self.network_code + '_' + self.code

    def get_n_active_channels(self, session, last_datetime):
        self.n_active_channels = None # session.query() # 
        if self.n_active_channels == 0:
            self.active = 0
            self.lastactive = last_datetime


class Channel(Base):
    __tablename__ = "channel"

    uni_code = Column(String(12), primary_key=True, unique=True)
    station_code = Column(String(8), ForeignKey('station.code'))
    code = Column(String(3))
    type = Column(String(1)) # 'D', 'C', 'E', 'T', 'O', 'L'
    sensor_description = Column(String(80))
    sample_rate = Column(Float)
    begintime = Column(DateTime())
    endtime = Column(DateTime())
    active = Column(Boolean())

    #station = relationship("Station", backref="channel")

    def __init__(self, **columns):
        self.__dict__.update(columns)
        self.station_code = self.network_code + '_' + self.station_code
        self.uni_code = self.station_code + ':' + self.code


class ChannelDiff(Base):
    __tablename__ = "channel_diff"

    id = Column(Integer, primary_key=True)
    uni_code = Column(String(12), ForeignKey('channel.uni_code'))
    diff = Column(Boolean) # True == activated, False == removed
    time_id = Column(Integer, ForeignKey('access_time.id'))

    def __init__(self, **columns):
        self.__dict__.update(columns)


class Missing(Base):
    __tablename__ = "missing"

    id = Column(Integer, primary_key=True)
    tablename = Column(String(12))
    code = Column(String(12))
    time_id = Column(Integer, ForeignKey('access_time.id'))

    def __init__(self, **columns):
        self.__dict__.update(columns)


class AccessTime(Base):
    __tablename__ = "access_time"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    type = Column(Integer)