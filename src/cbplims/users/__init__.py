from cbplims import app
from flask import g
from collections import namedtuple

User = namedtuple('user', 'username fullname is_global_admin')


def is_user_global_admin(uid):
    cur = g.dbconn.cursor()
    cur.execute('SELECT id, is_global_admin FROM users WHERE id = %s', (uid,))
    record = cur.fetchone()
    cur.close()

    if not record or not record[1]:
        return False
    return True


def get_users():
    cur = g.dbconn.cursor()
    c = 'SELECT username,fullname,is_global_admin FROM users'
    cur.execute(c)
    users = []
    for record in cur:
        app.logger.debug(str(record))
        users.append(User(record[0], record[1], record[2]))
    cur.close()

    return users


def get_t():
    user = []
    user.append(User(1, 2, 3))
    return user
