from seedlink import Seedlink
from query import QueryDB

import time
st = time.time()

""" Get live events from seedlink """
sl = Seedlink()
sl.get_stream_metadata()
sl.add_channels()
print(f'{len(sl.channels)} live channels gathered from seedlink')

""" Add Timestamp """
db = QueryDB()
time_id = db.add_access_time(sl.access_time)

""" Add change state channels """
db = QueryDB()
db_channels = db.get_channels()
db_active_codes = set()
db_inactive_codes = set()
for code, active in db_channels:
    if active:
        db_active_codes.add(code)
    else:
        db_inactive_codes.add(code)

dt = time.time()
db_actived_chan_codes = sl.chan_codes & db_inactive_codes
print(f'No. of activated channels in db {len(db_actived_chan_codes)}')
for code in db_actived_chan_codes:
    db.append_channel_diff(code, True, time_id)

remvd_chan_codes = db_active_codes - sl.chan_codes
print(f'Length of removed from active {len(remvd_chan_codes)}')
for code in remvd_chan_codes:
    db.append_channel_diff(code, False, time_id)

db.add_channel_diffs()
print(f'Time to insert channel diffs {time.time()-dt:.2f}s')

""" Update channel.active state """
dt = time.time()
db.update_active_channels(db_actived_chan_codes, active=True)
db.update_active_channels(remvd_chan_codes, active=False)
print(f'Time to update channel active {time.time()-dt:.2f}s')
db.close()

t = time.time()-st; t_mins = int(t/60); t_secs = int(t - t_mins*60)
print(f'Runtime {t_mins}m {t_secs}s')
