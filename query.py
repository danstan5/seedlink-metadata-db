from tables import Network, Station, Channel, Missing, UpdateTime
from base import Session

class QueryDB():
    def __init__(self):
        self.session = Session()

    def get_last_update(self):
        self.prv_time = self.session.query(UpdateTime).order_by(UpdateTime.id.desc()).first()
        return self.prv_time
    
    def get_channels(self):
        self.channels = self.session.query(Channel).all()
        return self.channels

    def get_codes(self):
        self.chan_codes = set([i[0] for i in self.session.query(Channel.uni_code).all()])
        self.sta_codes = set([i[0] for i in self.session.query(Station.code).all()])
        self.net_codes = set([i[0] for i in self.session.query(Network.code).all()])

    def add_missing(self, tablename, code):
        if not self.session.query(Missing).filter(
            Missing.tablename == tablename,
            Missing.code == code
        ).count():
            self.session.add(Missing(tablename=tablename, code=code))

    def update_channel_actives(self, station_codes, active):
        """ change to via query rather than with ORM """
        for sta in station_codes:
            self.session.query(Channel).\
                filter(Channel.uni_code == sta).\
                update({"active" : active})

    def add_update_time(self, access_time):
        timestamp = UpdateTime(datetime=access_time)
        self.session.add(timestamp)
        return timestamp

    def close_connection(self):
        self.session.close()
