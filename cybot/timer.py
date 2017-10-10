from .dbwrapper import SQLite
from datetime import datetime, timedelta


class Timer(SQLite):

    def __init__(self, username, category):
        self.table = 'timer'
        self.username = username
        self.conditions = 'username = "{0}"'.format(
            username)
        self.category = category
        self.connect('db/bot.db')
        tabledata = {'username': 'text', 'category': 'text',
                     'last': 'timestamp', '': 'UNIQUE(username, category) ON CONFLICT REPLACE'}
        self.maketable(self.table, tabledata)

    def check(self, timeout, category=None):
        last = self.getTimer(category if category else self.category)
        ret = {'ready': False}
        if last:
            last = datetime.strptime(last[0], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            td = timedelta(seconds=timeout)
            if(now - last > td):
                ret['ready'] = True
            else:
                ret['timetil'] = int(((last + td) - now).total_seconds())
                ret['ready'] = False
        else:
            ret['ready'] = True
            self.setTimer(category)
        return ret

    def setTimer(self, category=None, last=None):
        data = {'username': self.username,
                'last': '#!datetime("now", "localtime")', 'category': category if category else self.category}
        if last:
            data['last'] = last
        self.write(self.table, data)

    def getTimer(self, category=None):
        conditions = ['category="{}"'.format(
            category if category else self.category)]
        timerData = self.get('last', single=True, conditions=conditions)
        return timerData

    def raw(self, category=None, last=None, username=None):
        cond = []
        if category:
            cond.append('category = "{}"'.format(category))
        if last:
            cond.append('last = "{}"'.format(last))
        if username:
            cond.append('username = "{}"'.format(username))
        if(len(cond) > 0):
            return self.get('*', conditions=cond)
        return self.get('*')

    def get(self, columns, single=False, conditions=None, limit=None):
        formCond = self.conditions
        if conditions:
            formCond = '{} AND {}'.format(
                self.conditions, ' and '.join(conditions) if conditions else '')
        qry = 'SELECT {0} FROM {1} WHERE {2};'.format(
            columns, self.table, formCond)
        self.query(qry)
        if single:
            rows = self.cursor.fetchone()
        else:
            rows = self.cursor.fetchall()
        if rows:
            return rows[len(rows) - limit if limit else 0:]
        return []

    def update(self, data):
        dqry = ''
        for k, v in data.items():
            dqry += '{}={},'.format(k, v)
        dqry = dqry[:-1]
        qry = 'UPDATE {0} SET {1} WHERE {2}'.format(
            self.table, dqry, self.conditions)
        self.query(qry)
