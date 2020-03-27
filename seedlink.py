from datetime import datetime as dt
from obspy.clients.seedlink.easyseedlink import create_client
import xml.etree.ElementTree as ET
import pandas as pd

from tables import Channel

class Seedlink():
    def __init__(self):
        self.servers = {
            #'gfz':'geofon.gfz-potsdam.de:18000',
            'iris':'rtserve.iris.washington.edu:18000',
            #'nz':'link.geonet.org.nz:18000'
            }

    def create_client(self, uri):
        self.client = create_client(uri)

    def get_stream_metadata(self):
        for server, uri in self.servers.items():
            self.create_client(uri)
            stream_metadata = self.client.get_info('STREAMS')
            self.stream = ET.fromstring(stream_metadata)
            self.access_time = dt.utcnow()

    def add_channels(self):
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
                self.channels[chan.uni_code] = chan
                self.net_codes.add(chan.network_code)
                self.sta_codes.add(chan.station_code)
                self.chan_codes.add(chan.uni_code)
            # TEMP
            # if len(self.channels) > 15000:
            #     break
