import os
from psycopg2.pool import ThreadedConnectionPool


class _wrapped_conn(object):
    def __init__(self, pool):
        self.pool = pool
        self.conn = None

    def __enter__(self):
        self.conn = self.pool.getconn()
        print "enter conn... %s" % self.conn
        return self.conn

    def __exit__(self, type, value, traceback):
        print "exit conn..."
        self.pool.putconn(self.conn)


class Config(dict):
    def __init__(self):
        dict.__init__(self)
        self._pool = None

    def get_db_conn(self):
        if not self._pool:
            self._pool = ThreadedConnectionPool(1, 5, database=self['DB_NAME'], user=self['DB_USER'], password=self['DB_PASS'], host=self['DB_HOST'], port=self['DB_PORT'])
            self.test()
        return self._pool.getconn()

    def put_db_conn(self, conn):
        self._pool.putconn(conn)

    def conn(self):
        if not self._pool:
            self._pool = ThreadedConnectionPool(1, 5, database=self['DB_NAME'], user=self['DB_USER'], password=self['DB_PASS'], host=self['DB_HOST'], port=self['DB_PORT'])
            self.test()

        return _wrapped_conn(self._pool)

    def test(self):
        print "testing..."
        init = False
        with self.conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT value FROM meta_kv WHERE key = 'ping';")
                val = cur.fetchone()
                if val[0] != 'pong':
                    init = True
            except:
                init = True
        cur.close()
        conn.rollback()

        if init:
            self.initdb()

    def initdb(self):
        with self.conn() as conn:
            print "init-db"
            cur = conn.cursor()
            with open('db/schema.sql') as f:
                buf = ''
                for line in f:
                    if '--' in line:
                        line = line[:line.find('--')]

                    line = line.strip()

                    if buf:
                        buf += ' ' + line
                    else:
                        buf = line

                    if buf and buf[-1] == ';':
                        print buf
                        cur.execute(buf)
                        buf = ''

            cur.close()
            conn.commit()
            print "init-db-out"


def load_config(fnames=['../scripts/db.cred', '../app.config']):
    config = Config()
    for fname in fnames:
        if os.path.exists(fname):
            with open(fname) as f:
                for line in f:
                    k, v = line.strip().split('=', 1)
                    config[k] = v

    config['DB_HOST'] = 'localhost'
    config['DB_PORT'] = 5432

    if 'POSTGRES_PORT_5432_TCP_ADDR' in os.environ:
        config['DB_HOST'] = os.environ['POSTGRES_PORT_5432_TCP_ADDR']

    if 'POSTGRES_PORT_5432_TCP_PORT' in os.environ:
        config['DB_PORT'] = os.environ['POSTGRES_PORT_5432_TCP_PORT']

    return config
