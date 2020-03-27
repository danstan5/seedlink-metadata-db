import psycopg2 as pg
from psycopg2.extras import execute_values
from db_config import DB_Config

db_config = DB_Config()
conn = db_config.get_section('postgres_rds')

class QueryDB():
    def __init__(self):
        self.conn = pg.connect(**conn)
        self.cur = self.conn.cursor()

    def execute_update_active_channels(self, codes, active):
        if active:
            sql = 'UPDATE channel SET active = true WHERE uni_code IN %s'
        else:
            sql = 'UPDATE channel SET active = false WHERE uni_code IN %s'
        self.cur.execute(sql, (tuple(codes),))
        assert self.cur.rowcount == len(codes), 'No. of channels to update not matching expected'
        self.conn.commit()

    def close(self):
        self.cur.close()
        if self.conn is not None:
            self.conn.close()