import os, sys
sys.path.append(os.getcwd())

from clients.seedlink import Seedlink
from db.database import Database

import logging, logger
log = logging.getLogger(__name__)

log.info('Start set active seedlinks script')

""" Get live events from seedlink """
sl = Seedlink('iris')
sl.get_stream_metadata()
sl.add_channels()

""" Add Timestamp """
db = Database()
time_id = db.add_access_time(sl.access_time)

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

db_actived_codes = sl.chan_codes & db_inactive_codes
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
