import sqlite3 as sql


class SQLite:

    def __init__(self, name=None):
        self.connection = None
        self.cursor = None
        if(name):
            self.connect(name)
            self.createtables()

    def connect(self, name):
        self.connection = sql.connect(name)
        self.cursor = self.connection.cursor()
        return self.connection

    def createtables(self):
        qry = '''CREATE TABLE IF NOT EXISTS wallet (username text UNIQUE, amount real, lasthandout timestamp)'''
        self.query(qry)

    def get(self, table, columns, conditions=None, limit=None):
        qry = 'SELECT {0} FROM {1}{2};'.format(
            columns, table,
            ' WHERE {}'.format(conditions) if conditions else '')
        self.query(qry)

        rows = self.cursor.fetchall()
        return rows[len(rows) - limit if limit else 0:]

    def write(self, table, data):
        columns = []
        values = []
        for k, v in data.items():
            columns.append('"' + str(k) + '"')
            values.append('"' + str(v) + '"')
        qry = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(
            table, ', '.join(columns), ', '.join(values))
        return self.query(qry)

    def update(self, table, data, conditions=None):
        data = ''
        for k, v in data.items():
            data += '{}={},'.format(k, v)
        data = data[:-1]
        qry = 'UPDATE {0} SET {1} {2}'.format(
            table, data, ' WHERE {}'.format(conditions) if conditions else '')
        return self.query(qry)

    def query(self, sql, commit=True):
        cmd = self.cursor.execute(sql)
        if commit:
            self.connection.commit()
        return cmd
