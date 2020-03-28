from tables import Network, Station, Channel, Missing, AccessTime
from base import Session

class QueryDB():
    def __init__(self):
        self.session = Session()

    def get_last_update_time(self):
        self.prv_time = self.session.query(AccessTime).order_by(AccessTime.id.desc()).first()
        return self.prv_time.datetime
    
    def get_channels(self):
        self.channels = self.session.query(Channel).all()
        return self.channels

    def get_codes(self):
        self.chan_codes = set([i[0] for i in self.session.query(Channel.uni_code).all()])
        self.sta_codes = set([i[0] for i in self.session.query(Station.code).all()])
        self.net_codes = set([i[0] for i in self.session.query(Network.code).all()])

    def add_missing(self, tablename, code, access_time_id):
        update = self.session.query(Missing).\
            filter(
                Missing.tablename==tablename,
                Missing.code==code
                ).\
            update({'time_id' : access_time_id})
        if not update:
            missing = Missing(
                tablename=tablename,
                code=code,
                time_id=access_time_id,
                )
            self.session.add(missing)

    def update_channel_actives(self, station_codes, active):
        """ change to via query rather than with ORM """
        for sta in station_codes:
            self.session.query(Channel).\
                filter(Channel.uni_code == sta).\
                update({"active" : active})

    def add_access_time(self, datetime, type=1):
        accesstime = AccessTime(
            datetime=datetime,
            type=type,
        )
        self.session.add(accesstime)
        return accesstime.id

    def close_connection(self):
        self.session.close()
