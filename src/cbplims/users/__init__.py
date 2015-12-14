from cbplims import app
import cbplims.auth

from flask import g
from collections import namedtuple

User = namedtuple('user', 'id username fullname is_global_admin is_active allow_password_change')


def get_users():
    cur = g.dbconn.cursor()
    c = 'SELECT id, username,fullname,is_global_admin,is_active,allow_password_change FROM users ORDER BY is_active DESC, username'
    cur.execute(c)
    users = []
    for record in cur:
        users.append(User(*record))
    cur.close()

    return users


def get_user(uid):
    cur = g.dbconn.cursor()
    sql = 'SELECT id, username, fullname, is_global_admin, is_active, allow_password_change FROM users WHERE id = %s'
    cur.execute(sql, (uid,))
    record = cur.fetchone()
    if not record:
        return None

    user = User(*record)
    cur.close()

    return user


def add_user(fullname, username, password, is_admin, allow_password_change):
    cur = g.dbconn.cursor()
    sql = 'INSERT INTO users (id,username, fullname, password, is_global_admin, allow_password_change) VALUES (DEFAULT,%s,%s,%s,%s,%s) RETURNING id'
    pwd = cbplims.auth.auth_pbkdf2.generate_new_password_string(password)

    # normally I use "try" and then a rollback if it does not work.
    # don't know where the loggers are?
    # app.logger.audti?

    app.logger.debug("Adding new user: %s, %s, %s, %s", fullname, username, is_admin, allow_password_change)

    cur.execute(sql, (username, fullname, pwd, is_admin, allow_password_change))
    row = cur.fetchone()
    user_id = row[0]

    g.dbconn.commit()
    cur.close()

    return user_id


def edit_user(user_id, full_name, passwd, is_admin=None, allow_password_change=None):
    app.logger.debug("Updating user (%s): %s, %s, %s", user_id, full_name, is_admin, allow_password_change)

    cur = g.dbconn.cursor()

    sql = 'UPDATE users SET fullname=%s, '
    args = [full_name, ]

    if is_admin is not None:
        sql += 'is_global_admin=%s, allow_password_change=%s'
        args.append(is_admin)
        args.append(allow_password_change)

    if passwd:
        app.logger.debug("Updating user password (%s)", user_id)
        pwd = cbplims.auth.auth_pbkdf2.generate_new_password_string(passwd)

        sql += ', password=%s'
        args.append(pwd)

    args.append(user_id)
    sql += ' WHERE id=%s'

    app.logger.debug("SQL: %s (%s)", sql, ','.join([str(x) for x in args]))

    cur.execute(sql, args)

    # normally I use "try" and then a rollback if it does not work.
    # don't know where the loggers are?
    # app.logger.audti?

    g.dbconn.commit()
    cur.close()


def del_user(uid):
    app.logger.debug("Deleting user: %s", uid)

    cur = g.dbconn.cursor()
    sql = 'DELETE FROM users WHERE id = %s '
    cur.execute(sql, (uid,))
    g.dbconn.commit()
    cur.close()
    return True


def disable_user(uid):
    app.logger.debug("Disabling user: %s", uid)

    cur = g.dbconn.cursor()
    sql = 'UPDATE users SET is_active=FALSE WHERE id = %s '
    cur.execute(sql, (uid,))
    g.dbconn.commit()
    cur.close()
    return True


def enable_user(uid):
    app.logger.debug("Enabling user: %s", uid)

    cur = g.dbconn.cursor()
    sql = 'UPDATE users SET is_active=TRUE WHERE id = %s '
    cur.execute(sql, (uid,))
    g.dbconn.commit()
    cur.close()
    return True
