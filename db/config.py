import os
from configparser import ConfigParser

import logging, logger
log = logging.getLogger(__name__)

class Config():
    def __init__(self,
        section = 'postgres',
        configfile = 'db_config.ini',
        check_vars: list = ['host','user','password','database']
    ):
        self.parser = ConfigParser()
        self.section = section
        if not self.parser.read(configfile):
            self.write_env_variables(configfile)
            self.parser.read(configfile)
        self._check_section_exists(self.section)
        self._check_args_set(check_vars)
    
    def write_env_variables(self, file):
        log.info('Writting env variables to configfile')
        self.parser[self.section] = {
            'host':os.environ.get('DB_HOST') or "",
            'user':os.environ.get('DB_USERNAME') or "",
            'password':os.environ.get('DB_PASSWORD') or "",
            'database':os.environ.get('DB_DATABASE') or "seedlink_metadata_db",
            'port':os.environ.get('DB_PORT') or "5432"}
        with open(file, 'w') as configfile:
            self.parser.write(configfile)

    def _check_section_exists(self, section):
        if not self.parser.has_section(section):
            log.exception(f'Coudn\'t find database config section "{section}".')
            raise SystemExit

    def _check_args_set(self, args):
        exceptions=0
        for arg in args:
            try:
                if self.parser.get(self.section, arg) == (None or ""):
                    raise KeyError
            except:
                log.exception(f'Variable "{arg}" was missing from db config')
                exceptions += 1
        if exceptions:
            raise SystemExit

    def get_dict(self) -> dict:
        return dict(self.parser.items(self.section))

    def get_conn_str(self) -> str:
        host = self.parser.get(self.section, 'host')
        user = self.parser.get(self.section, 'user')
        password = self.parser.get(self.section, 'password')
        database = self.parser.get(self.section, 'database')
        return f'postgresql://{user}:{password}@{host}/{database}'
