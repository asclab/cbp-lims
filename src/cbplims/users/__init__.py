from cbplims import conf
from collections import namedtuple
Users = namedtuple('users', 'username fullname is_global_admin')

def is_user_global_admin(uid):
    with conf.conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, is_global_admin FROM users WHERE id = %s', (uid,))
        record = cur.fetchone()
        cur.close()

        if not record or not record[1]:
            return False
        return True


def get_users():
    with conf.conn() as conn:
        cur = conn.cursor()
        c = 'SELECT username,fullname,is_global_admin FROM users'
        cur.execute(c)
        users = []
        for record in cur:
            print record
            users.append(Users(record[0], record[1], record[2]))
        cur.close()

        return users

def get_t():
    user = []
    user.append(Users(1,2,3))
    return user
