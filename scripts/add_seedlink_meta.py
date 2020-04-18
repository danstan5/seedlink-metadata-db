import os, sys
sys.path.append(os.getcwd())

from clients.seedlink import Seedlink
from clients.fsdn_routing import Metadata
from db.database import Database
from db.orm.database import Database as AlchemyDatabase

import logging, logger
log = logging.getLogger(__name__)

log.info('Start add active seedlinks metadata to db')

""" Connect to database """
db = AlchemyDatabase()
db.get_codes()

""" Get live events from seedlink """
sl = Seedlink('iris')
sl.get_stream_metadata()
sl.add_channels()

# new codes set, for codes not in db
net_codes = sl.net_codes - db.net_codes
sta_codes = sl.sta_codes - db.sta_codes
chan_codes = sl.chan_codes - db.chan_codes
log.info(
    f'Seedlink vs existing db:'
    f' {len(net_codes)} new networks,'
    f' {len(sta_codes)} new stations,'
    f' {len(chan_codes)} new channels'
)

""" Add Timestamp """
time_id = db.add_access_time(sl.access_time)

""" Add new channels, stations, networks or missing metadata """
if len(chan_codes) > 0:
    added_networks = set()
    added_stations = set()
    added_chan_codes = set()
    channel_metadata = set()
    
    """ Get iris metadata """
    iris_meta = Metadata(routing_client='iris-federator')
    iris_meta.get_inventory(net_codes, sta_codes)

    # add new networks
    for network_code in net_codes: 
        network = iris_meta.create_network_cls(network_code)
        if network:
            db.session.add(network)
            added_networks.add(network_code)
        else:
            db.add_missing("network", network_code, time_id)
    db.session.commit()
    log.info(
        f'{len(net_codes)} new sl networks, '
        f'{len(added_networks)} avaliable from iris added to db')

    # add new stations
    for station_code in sta_codes: 
        station = iris_meta.create_station_cls(station_code)
        if station:
            db.session.add(station)
            added_stations.add(station_code)
        else:
            db.add_missing("station", station_code, time_id)
    db.session.commit()
    log.info(
        f'{len(sta_codes)} new sl stations, '
        f'{len(added_stations)} avaliable from iris added to db')
    
    # add new channels
    new_channels = [sl.channels[code] for code in chan_codes]
    all_stations = added_stations | db.sta_codes
    for channel in new_channels:
        if channel.station_code in all_stations:
            if iris_meta.add_channel_meta(channel):
                channel_metadata.add(channel.uni_code)
            db.session.add(channel)
            added_chan_codes.add(channel.uni_code)
    db.session.commit()
    log.info(
        f'{len(new_channels)} new sl channels, '
        f'{len(channel_metadata)} had metadata added from iris, '
        f'{len(added_chan_codes)} added to db')

db.close_connection() # close sqlalchemy conn for faster psycopg2

""" Add channel state changes to diff """
db = Database()
db_channels = db.get_channels()
db_active_codes = set()
db_inactive_codes = set()
for code, active in db_channels:
    if active:
        db_active_codes.add(code)
    else:
        db_inactive_codes.add(code)

db_actived_codes = (sl.chan_codes & db_inactive_codes) | added_chan_codes
for code in db_actived_codes:
    db.append_channel_diff(code, True, time_id)

db_remvd_codes = db_active_codes - sl.chan_codes
for code in db_remvd_codes:
    db.append_channel_diff(code, False, time_id)

db.add_channel_diffs()

""" Update channel.active """
db.update_active_channels(db_actived_codes, active=True)
db.update_active_channels(db_remvd_codes, active=False)

db.close()
log.info('Finished script')
