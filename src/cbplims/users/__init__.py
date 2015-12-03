from flask import g


def is_user_global_admin(uid):
    cur = g.dbconn.cursor()
    cur.execute('SELECT id, is_global_admin FROM users WHERE id = %s', (uid,))
    record = cur.fetchone()
    cur.close()

    if not record or not record[1]:
        return False
    return True
