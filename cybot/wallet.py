from .dbwrapper import SQLite
from datetime import datetime, timedelta


class Wallet(SQLite):

    def __init__(self, username):
        self.creation = False
        self.table = 'wallet'
        self.username = username
        self.conditions = 'username = "{0}"'.format(username)
        self.connect('db/currency.db')
        self.maketables()
        if not self.usercheck():
            data = {'username': username, 'amount': 0,
                    'lasthandout': '#!datetime("now", "localtime")'}
            self.write(self.table, data)
            self.creation = True

    def maketables(self):
        qry = '''CREATE TABLE IF NOT EXISTS wallet (username text UNIQUE, amount real, lasthandout timestamp)'''
        self.query(qry)

    def usercheck(self):
        return self.get('*')

    @property
    def balance(self):
        return int(self.get('amount', True)[0])

    @property
    def lasthandout(self):
        return self.get('lasthandout', True)[0]

    def transaction(self, amount):
        data = {'amount': (amount + self.balance)}
        self.update(data)

    def handout(self, amount):
        self.transaction(amount)
        self.update({
            'lasthandout': 'datetime("now", "localtime")'})

    def get(self, columns, single=False, limit=None):
        qry = 'SELECT {0} FROM {1} WHERE {2};'.format(
            columns, self.table, self.conditions)
        self.query(qry)
        if single:
            rows = self.cursor.fetchone()
        else:
            rows = self.cursor.fetchall()
        if rows:
            return rows[len(rows) - limit if limit else 0:]
        return False

    def update(self, data):
        dqry = ''
        for k, v in data.items():
            dqry += '{}={},'.format(k, v)
        dqry = dqry[:-1]
        qry = 'UPDATE {0} SET {1} WHERE {2}'.format(
            self.table, dqry, self.conditions)
        self.query(qry)
