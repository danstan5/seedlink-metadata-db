from obspy.clients.fdsn import RoutingClient
from obspy.core import UTCDateTime

from tables import Network, Station

class Metadata():
    def __init__(self):
        self.r_client = RoutingClient("iris-federator")

    def _codes_to_str(self, unique_codes):
        nets, stas = set(), set()
        for code in unique_codes:
            net, sta = code.split('_')
            nets.add(net)
            stas.add(sta)
        print(f'Querying {len(nets)} networks, {len(stas)} stations')
        self.nets = ",".join(nets) # set -> str
        self.stas = ",".join(stas) # set -> str

    def get_inventory(self, sta_codes):
        """ 
        Return an inventory object of all stations in IRIS
        : can be queried by networks and stations
        """
        try:
            assert len(sta_codes) < 150 , 'Comment: too many stations to query on'
            self._codes_to_str(sta_codes)
            self.inventory = self.r_client.get_stations(
                network=self.nets,
                station=self.stas,
                starttime=UTCDateTime.now()-60,
            )
        except Exception as e:
            print(e)
            self.inventory = self.r_client.get_stations(
                starttime=UTCDateTime.now()-60)
        print(f'No of networks downloaded = {len(self.inventory.networks)}.')

    def _get_network(self, network_code):
        for network in self.inventory.networks:
            if network.code == network_code:
                self.network = network
                return network
        self.network = None

    def _get_station(self, station_code):
        net_code, sta_code = station_code.split('_')
        if not self._get_network(net_code):
            return
        for station in self.network:
            if station.code == sta_code:
                self.station = station
                return station
        self.station = None
    
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
