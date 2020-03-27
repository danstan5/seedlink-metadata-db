from seedlink import Seedlink
from iris import Metadata
from postgres import QueryDB
from query import QueryDB as OrmQueryDB
from tables import ChannelDiff

import time
st = time.time()

""" Connect to database """
db = OrmQueryDB()
db.get_codes()

""" Get live events from seedlink """
sl = Seedlink()
sl.get_stream_metadata()
sl.add_channels()
print(f'{len(sl.channels)} live channels gathered from seedlink')

# new codes set, for codes not in db
net_codes = sl.net_codes - db.net_codes
sta_codes = sl.sta_codes - db.sta_codes
chan_codes = sl.chan_codes - db.chan_codes
print(f'Seedlink vs existing db:'
      f' {len(net_codes)} new networks,'
      f' {len(sta_codes)} new stations,'
      f' {len(chan_codes)} new channels')

""" Add Timestamp """
accesstime = db.add_access_time(sl.access_time)

""" Add new channels, stations, networks or missing metadata """
if len(chan_codes) > 0:
    added_networks = set()
    added_stations = set()
    added_chan_codes = set()
    channel_metadata = set()
    
    """ Get iris metadata """
    iris_meta = Metadata()
    iris_meta.get_inventory(net_codes, sta_codes)

    for network_code in net_codes: # add new networks
        network = iris_meta.create_network_cls(network_code)
        if network:
            db.session.add(network)
            added_networks.add(network_code)
        else:
            db.add_missing("network", network_code, accesstime.id)
    db.session.commit()
    print(f'{len(net_codes)} new sl networks')
    print(f'{len(added_networks)} avaliable from iris, added to db')

    for station_code in sta_codes: # add new stations
        station = iris_meta.create_station_cls(station_code)
        if station:
            db.session.add(station)
            added_stations.add(station_code)
        else:
            db.add_missing("station", station_code, accesstime.id)
    db.session.commit()
    print(f'{len(sta_codes)} new sl stations')
    print(f'{len(added_stations)} avaliable from iris, added to db')
    
    dt=time.time()
    new_channels = [sl.channels[code] for code in chan_codes]
    all_stations = added_stations | db.sta_codes
    for channel in new_channels:  # add new channels
        if channel.station_code in all_stations:
            if iris_meta.add_channel_meta(channel):
                channel_metadata.add(channel.uni_code)
            db.session.add(channel)
            added_chan_codes.add(channel.uni_code)
    print(f'{len(new_channels)} new sl channels')
    print(f'{len(channel_metadata)} had metadata added from iris')
    print(f'{len(added_chan_codes)} added to db')
    print(f'Time to get channels: {time.time()-dt}s')
    dt=time.time()
    db.session.commit()
    print(f'Time to commit channels: {time.time()-dt}s')

""" Add change state channels """ # TODO make this section run on psycopg2 #
db_channels = db.get_channels()
db_active_codes = set([c.uni_code for c in db_channels if c.active == True])
db_inactive_codes = set([c.uni_code for c in db_channels  if c.active == False])

# newly added to db + those not active last time now aval from seedlink
db_actived_chan_codes = sl.chan_codes & db_inactive_codes
print(f'No. of activated channels in db {len(db_actived_chan_codes)}')
for code in db_actived_chan_codes | added_chan_codes:
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

""" Commit all changes to the database """
db.session.commit()
db.close_connection()
print(f'Time to commit channel_diff : {time.time()-dt}s')

""" Update channel.active state """
db = QueryDB()
db.execute_update_active_channels(db_actived_chan_codes, active=True)
db.execute_update_active_channels(remvd_chan_codes, active=False)
db.close()

t = time.time()-st; t_mins = int(t/60); t_secs = int(t - t_mins*60)
print(f'Runtime {t_mins}m {t_secs}s')
