# authentication methods
import auth_pbkdf2
import binascii
from cbplims import conf


def authenticate(username, password):
    found_pass = None
    with conf.conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM users WHERE username = %s', (username,))
        record = cur.fetchone()
        cur.close()

    if not record:
        return False

    userid = record[0]
    found_pass = record[1]

    method, val = found_pass.split("$", 1)

    if method == 'pbkdf2':
        salt, hashed_passwd = val.split('$', 1)

        # PBDKF2_HMAC, using the embedded salt
        dk = auth_pbkdf2.backported_pbkdf2_hmac('sha256', password, salt, 100000)
        if secure_compare(hashed_passwd, binascii.hexlify(dk)):
            return userid
    elif method == 'krb5':
        #kerberos_name = val
        pass

    return None


def secure_compare(foo, bar):
    match = True
    for one, two in zip(foo, bar):
        if one != two:
            match = False

    return match
