import sys
from obspy.clients.fdsn import RoutingClient
from obspy.core import UTCDateTime

from db.orm.tables import Network, Station

import logging, logger
log = logging.getLogger(__name__)

class Metadata():
    def __init__(self, routing_client):
        self.r_client = self.create_client(routing_client)
    
    def create_client(self, routing_client):
        try:
            return RoutingClient(routing_client)
        except:
            log.error('Couldn\'t connect to %s' % routing_client)
            raise SystemExit

    def _codes_to_str(self, network_codes, station_codes):
        nets = set(network_codes)
        stas = set()
        for sta_code in station_codes:
            net, sta = sta_code.split('_')
            nets.add(net)
            stas.add(sta)
        return ",".join(nets), ",".join(stas) # set -> str

    def _get_inventory(self, **kwargs):
        kwargs['level'] = 'channel'
        kwargs['starttime'] = UTCDateTime.now()-60
        try:
            return self.r_client.get_stations(**kwargs)
        except Exception:
            log.error('Accessing inventory failed.\n \
                Data parsed: %s' % str(kwargs)
            )
            log.exception('Traceback: ')
            raise SystemExit

    def get_inventory(self, net_codes, sta_codes):
        """ 
        Return an inventory object for the routing server
        : can be queried by networks and stations
        """
        if len(sta_codes) == 0:
            log.warning('No station codes to add, can\'t get inventory')
            return
        if len(sta_codes) < 400:
            nets, stas = self._codes_to_str(net_codes, sta_codes)
            self.inventory = self._get_inventory(network=nets, station=stas)
        else:
            log.warning('%s is too many stations to query on' % len(sta_codes))
            self.inventory = self._get_inventory()
        log.info('No of networks downloaded %s' % len(self.inventory.networks))

    def _get_network(self, network_code):
        self.network = None
        for network in self.inventory.networks:
            if network.code == network_code:
                self.network = network
                return network

    def _get_station(self, station_code):
        net_code, sta_code = station_code.split('_')
        self.station = None
        if self._get_network(net_code):
            for station in self.network:
                if station.code == sta_code:
                    self.station = station
                    return station
    
    def _create_network_cls(self):
        return Network(
            code = self.network.code,
            startdate = self.network.start_date.datetime,
            description = self.network.description,
            n_total_stations = self.network.total_number_of_stations
        )

    def _create_station_cls(self):
        # note requires station and network to be set
        return Station(
            code = self.station.code,
            network_code = self.network.code,
            startdate = self.station.start_date.datetime,
            sitename = self.station.site.name,
            elevation = self.station.elevation,
            latitude = self.station.latitude,
            longitude = self.station.longitude,
            n_total_channels = self.station.total_number_of_channels
        )

    def create_network_cls(self, network_code):
        self._get_network(network_code)
        if self.network:
            return self._create_network_cls()

    def create_station_cls(self, station_code):
        self._get_station(station_code)
        if self.network != None and self.station != None:
            station = self._create_station_cls()
            return station

    def _get_channel(self, channel_code):
        self.channel = None
        station_code, chan_code = channel_code.split(':')
        if self._get_station(station_code):
            for channel in self.station:
                if channel.code == chan_code:
                    self.channel = channel
                    return channel

    def add_channel_meta(self, channel):
        channel.sensor_description = None
        channel.sample_rate = None
        if self._get_channel(channel.uni_code):
            if self.channel.sensor:
                channel.sensor_description = self.channel.sensor.description
            channel.sample_rate = self.channel.sample_rate
            return True