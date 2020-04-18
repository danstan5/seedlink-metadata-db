#import sys
from datetime import datetime as dt
from obspy.clients.seedlink.easyseedlink import create_client as easy_create_client
import xml.etree.ElementTree as ET

# dependancy requires connecting sqlalchemy - TODO removed from seedlink scope
from db.orm.tables import Channel

import logging, logger
log = logging.getLogger(__name__)

SERVERS = {
    'gfz':'geofon.gfz-potsdam.de:18000',
    'iris':'rtserve.iris.washington.edu:18000',
    'nz':'link.geonet.org.nz:18000'
}

class Seedlink():
    def __init__(self, server_name: str):
        self.server = SERVERS.get(server_name)
        if not self.server:
            exception_msg = '%s not accepted as server name, check clients.seedlink names' % server_name
            log.exception(exception_msg)
            raise SystemExit
        self.create_client(self.server)

    def create_client(self, server):
        try:
            self.client = easy_create_client(server)
        except:
            log.exception('Seedlink server wasn\'t created.')
            raise SystemExit

    def get_stream_metadata(self):
        try:
            meta_stream = self.client.get_info('STREAMS')
        except:
            log.exception('Could not get stream information.')
            raise SystemExit
        log.info('STREAMS added')
        self.stream = ET.fromstring(meta_stream)
        self.access_time = dt.utcnow()

    def add_channels(self, limit=None):
        self.channels = {}
        self.net_codes = set()
        self.sta_codes = set()
        self.chan_codes= set()
        for station in self.stream:
            for channel in station:
                chan = Channel(
                    network_code = station.attrib.get("network"),
                    station_code = station.attrib.get("name"), # converted unique for channels
                    code = channel.attrib.get("seedname"), # note: foreign key ID field == station_code + code
                    type = channel.attrib.get('type'),
                    begintime = dt.strptime(channel.attrib.get('begin_time'), "%Y-%m-%d %H:%M:%S"),
                    endtime = dt.strptime(channel.attrib.get('end_time'), "%Y-%m-%d %H:%M:%S"),
                    active = 1)
                self.net_codes.add(chan.network_code)
                self.sta_codes.add(chan.station_code)
                self.chan_codes.add(chan.uni_code)
                self.channels[chan.uni_code] = chan
            if limit:
                if len(self.channels) > limit:
                    break
        log.info(f'{len(self.channels)} total channels added from seedlink')
