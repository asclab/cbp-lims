import os.path
import logging
from collections import namedtuple

LogRecord = namedtuple('LogRecord', 'id, tstamp, level, filename, funcname, lineno, msg')


class DBLogger(logging.Handler):
    def __init__(self, conn, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self._conn = conn

    def close(self):
        self._conn.close()
        logging.Hander.close(self)

    def emit(self, record):
        sql = 'INSERT INTO logger (level, filename, funcname, lineno, msg) VALUES (%s, %s, %s, %s, %s)'
        cur = self._conn.cursor()
        cur.execute(sql, (record.levelname, os.path.relpath(record.pathname), record.funcName, record.lineno, record.getMessage()))
        self._conn.commit()
        cur.close()

    def fetch_messages(self, last_id=None, max_lines=100):
        sql = 'SELECT id, msg_ts, level, filename, funcname, lineno, msg FROM logger'
        args = []
        if last_id:
            sql += ' WHERE id > %s'
            args.append(last_id)

        sql += ' ORDER BY msg_ts DESC'

        if not last_id and max_lines:
            sql += ' LIMIT %s'
            args.append(max_lines)

        cur = self._conn.cursor()
        cur.execute(sql, args)

        records = []

        for record in cur:
            records.append(LogRecord(*record))

        return records[::-1]
