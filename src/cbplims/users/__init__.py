from cbplims import app
import cbplims.auth

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


def add_user(full_name,username,email,is_admin,pwd):
    cur = g.dbconn.cursor()
    sql = 'INSERT INTO users (id,username, fullname, password, is_global_admin) VALUES (DEFAULT,%s,%s,%s,%s)'
    pwd = cbplims.auth.auth_pbkdf2.generate_new_password_string(pwd)
    # normally I use "try" and then a rollback if it does not work.
    # don't know where the loggers are?
    # app.logger.audti? 
    cur.execute(sql, (username,full_name,pwd,is_admin) )
    g.dbconn.commit()
    cur.close()
    return True
