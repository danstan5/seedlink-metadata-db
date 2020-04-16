from configparser import ConfigParser

class DB_Config():
    def __init__(self):
        self.parser = ConfigParser()
        self.parser.read('database.ini')

    def _check_section_exists(self, section):
        if self.parser.has_section(section):
            return True
        raise Exception(f'Coudn\'t find database config section "{section}".')

    def get_url_conn_str_form(self, section) -> str:
        if not self._check_section_exists(section):
            print('Section doesnt exist.')
            return
        host = self.parser.get(section, 'host')
        user = self.parser.get(section, 'user')
        password = self.parser.get(section, 'password')
        database = self.parser.get(section, 'database')
        return f'postgresql://{user}:{password}@{host}/{database}'

    def get_section(self, section) -> dict:
        if self._check_section_exists(section):
            return dict(self.parser.items(section))