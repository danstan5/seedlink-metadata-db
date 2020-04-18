import psycopg2 as pg
from psycopg2.extras import execute_values
from db.config import Config
import traceback
import logging, logger
log = logging.getLogger(__name__)

config = Config()
conn =  config.get_dict()

class Database():
    def __init__(self):
        self.conn = pg.connect(**conn)
        self.cur = self.conn.cursor()
        self.channel_diffs = []

    def get_channels(self):
        self.cur.execute('select uni_code, active from channel')
        return self.cur.fetchall()

    def add_access_time(self, datetime, type=0):
        sql = 'INSERT INTO access_time(datetime, type) VALUES (%s,%s) RETURNING id'
        self.cur.execute(sql, (datetime, type))
        id = self.cur.fetchone()
        self.conn.commit()
        log.info('commit Access time to db')
        return id[0]

    def update_active_channels(self, codes, active):
        if not len(codes) == 0:
            if active:
                sql = 'UPDATE channel SET active = true WHERE uni_code IN %s'
            else:
                sql = 'UPDATE channel SET active = false WHERE uni_code IN %s'
            self.cur.execute(sql, (tuple(codes),))
            assert self.cur.rowcount == len(codes), 'No. of channels to update not matching expected'
            self.conn.commit()
        log.info(f'commit {len(codes)} channels "active" update -> {"added" if active else "removed"}')

    def append_channel_diff(self, uni_code, diff, time_id):
        self.channel_diffs.append((uni_code, diff, time_id))

    def add_channel_diffs(self):
        sql = 'INSERT INTO channel_diff(uni_code, diff, time_id) VALUES %s'
        try:
            execute_values(self.cur, sql, self.channel_diffs)
            self.conn.commit()
            log.info(f'commit {len(self.channel_diffs)} channel diffs')
            self.channel_diffs = []
        except pg.Error:
            log.exception('Postgres error on committing channel diff')
        except:
            log.error("Uncaught exception: %s", traceback.format_exc())

    def close(self):
        self.cur.close()
        if self.conn is not None:
            self.conn.close()
