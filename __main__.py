from base import Session
from seedlink import Seedlink
from query import QueryDB
from iris import Metadata
from tables import ChannelDiff

import time
st = time.time()

""" Connect to database """
db = QueryDB()
db.get_codes()

""" Get live events from seedlink """
sl = Seedlink()
sl.get_stream_metadata()
sl.add_channels()
print(f'{len(sl.channels)} live channels gathered from seedlink')

# new codes set, for codes not in db
chan_codes = sl.chan_codes - db.chan_codes
net_codes = sl.net_codes - db.net_codes
sta_codes = sl.sta_codes - db.sta_codes
print(f'Add {len(net_codes)} new networks,'
      f' {len(sta_codes)} new stations,'
      f' {len(chan_codes)} new channels')

""" Add Timestamp """
accesstime = db.add_access_time(sl.access_time)

""" 
Add new channels, stations, networks or missing metadata
"""
if len(chan_codes) > 0:
    missing_networks = set()
    missing_stations = set()
    added_chan_codes = set()
    iris_meta = Metadata()
    """ Get iris metadata """
    iris_meta.get_inventory(sta_codes)

    for network_code in net_codes: # add new networks
        network = iris_meta.create_network_cls(network_code)
        if network:
            db.session.add(network)
        else:
            db.add_missing("network", network_code, accesstime.id)
            missing_networks.add(network_code)
        
    for station_code in sta_codes: # add new stations
        station = iris_meta.create_station_cls(station_code)
        if station:
            db.session.add(station)
        else:
            db.add_missing("station", station_code, accesstime.id)
            missing_stations.add(station_code)

    new_channels = [sl.channels[code] for code in chan_codes]
    for channel in new_channels:  # add new channels
        if channel.station_code in missing_stations or \
           channel.network_code in missing_networks:
            db.add_missing("channel", channel.uni_code, accesstime.id)
        else:
            db.session.add(channel) # update links and add channel
            added_chan_codes.add(channel.uni_code)
    print(f'Length newly added to db {len(added_chan_codes)}')

""" Add change state channels """
db_channels = db.get_channels()
db_active_codes = set([c.uni_code for c in db_channels if c.active == True])
db_inactive_codes = set([c.uni_code for c in db_channels  if c.active == False])
print(f'Length inactive from db {len(db_inactive_codes)}')
print(f'Total channels in db {len(db_channels)}')

# newly added to db + those not active last time now aval from seedlink
actived_db_chan_codes = sl.chan_codes & db_inactive_codes
actived_chan_codes = added_chan_codes | actived_db_chan_codes
print(f'Length of activated {len(actived_chan_codes)}')
for code in actived_chan_codes:
    chan_diff = ChannelDiff(diff= True,
        uni_code=code, time_id=accesstime.id)
    db.session.add(chan_diff)

# were active in database not aval in seedlink data
remvd_chan_codes = db_active_codes - sl.chan_codes
print(f'Length of removed from active {len(remvd_chan_codes)}')
for code in remvd_chan_codes:
    chan_diff = ChannelDiff(diff= False,
        uni_code=code, time_id=accesstime.id)
    db.session.add(chan_diff)

""" Update Channel.active state """
db.update_channel_actives(actived_db_chan_codes, active=True)
db.update_channel_actives(remvd_chan_codes, active=False)
print('DONE')

""" Commit all changes to the database """
db.session.commit()
db.close_connection()

t = time.time()-st; t_mins = int(t/60); t_secs = int(t - t_mins*60)
print(f'Runtime {t_mins}m {t_secs}s')
