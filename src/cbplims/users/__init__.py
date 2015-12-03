from cbplims import app
from flask import g
from collections import namedtuple

User = namedtuple('user', 'id username fullname is_global_admin')


def get_users():
    cur = g.dbconn.cursor()
    c = 'SELECT id,username,fullname,is_global_admin FROM users'
    cur.execute(c)
    users = []
    for record in cur:
        app.logger.debug(str(record))
        users.append(User(*record))
    cur.close()

    return users


def get_user(uid):
    cur = g.dbconn.cursor()
    sql = 'SELECT id,username,fullname,is_global_admin FROM users WHERE id = %s'
    cur.execute(sql, (uid,))
    record = cur.fetchone()
    if not record:
        return None

    user = User(*record)
    app.logger.debug(str(user))
    cur.close()

    return user


def get_t():
    user = []
    user.append(User(1, 2, 3))
    return user
