from dbwrapper import SQLite
from datetime import datetime, timedelta


class Timer(SQLite):

    def __init__(self, username, category):
        self.table = 'timer'
        self.username = username
        self.conditions = 'username = "{0}"'.format(
            username)
        self.category = category
        self.connect('../db/bot.db')
        tabledata = {'username': 'text', 'category': 'text',
                     'last': 'timestamp UNIQUE(username, category, last) ON CONFLICT REPLACE'}
        self.maketables(
            self.table, tabledata)

    def setTimer(self, category, last=None):
        data = {'username': self.username,
                'last': '#!datetime("now", "localtime")', 'category': category}
        if last:
            data['last'] = last
        self.write(self.table, data)

    def check(self, category=None):
        catCond = category if category else self.category
        last = self.last(catCond)
        print(last)

    def last(self, category=None):
        if(category):
            return self.get('last', conditions='category="{}"'.format(category))[0]
        return self.get('last')[0]

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

    def reset(self, category=None, last=None):
        catCond = category if category else self.category
        data = {'last': 'datetime("now", "localtime")',
                'category': '"{}"'.format(catCond)}
        if last:
            data['last'] = last
        self.update(data)

    def get(self, columns, single=False, conditions=None, limit=None):
        formCond = self.conditions
        if conditions:
            formCond = '{} AND {}'.format(
                self.conditions, ' and '.join(conditions))
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


x = Timer('zim', 'handout')
print(x.last())
x.reset()
print(x.last())
x.setTimer('slots')
print(x.last('slots'))
print(x.raw())
