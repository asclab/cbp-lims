import os
import sys
import atexit
import logging
import binascii

from functools import wraps
from flask import Flask, redirect, render_template, session, g, request

import config
import support.uptime
import support.dblogger

conf = config.load_config()
conf.test()  # test the db connection and init db if needed


uptime = support.uptime.Uptime()


app = Flask(__name__)
app.secret_key = conf['SECRET_KEY'] if 'SECRET_KEY' in conf else binascii.hexlify(os.urandom(64))


### TODO: make this log to a configured filename
#import logging.handlers
#file_handler = logging.handlers.RotatingFileHandler(os.path.realpath('../working/cbplims.log'), backupCount=5, maxBytes=1000000)
#file_handler.setLevel(logging.DEBUG)
#app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

try:
    dblogger = support.dblogger.DBLogger(conf.build_db_conn())
    app.logger.addHandler(dblogger)
    atexit.register(dblogger.close)
except:
    sys.stderr.write("Unable to setup DB Logger!\n")


import users

app.logger.debug("Starting up Flask app")



# Let's just load a DB connection before each request
@app.before_request
def before_request_wrapper():
    if request.path == '/resetdb':
        return

    g.uptime = uptime.uptime_str()
    g.dbconn = conf.get_db_conn()

    g.is_project_admin = False
    g.is_project_view = False
    g.user = None
    g.project = None

    if 'uid' in session and session['uid']:
        g.user = users.get_user(session['uid'])

    if 'pid' in session and session['pid']:
        g.project = projects.get_project(session['pid'])
        if g.project:
            auth_level = projects.get_project_auth_level(g.user.id, g.project.id)
            if auth_level == 'admin':
                g.is_project_admin = True
            elif auth_level == 'view':
                g.is_project_view = True


# Be sure to close it
@app.teardown_request
def teardown_request_wrapper(err):
    if err:
        print "Error: %s " % err

    try:
        conf.put_db_conn(g.dbconn)
    except Exception, e:
        print e


# __tmp = app.handle_exception


# ## even if there is an exception
# def handle_exception_wrapper(*args, **kwargs):
#     try:
#         conf.put_db_conn(g.dbconn)
#     except Exception, e:
#         print e

#     return __tmp(*args, **kwargs)

# app.handle_exception = handle_exception_wrapper


# TODO: in the case we redirect, setup /signin, and /projects/choose
#       to redirect back to the original requested page. For example:
#       if we get a request for /samples/1, and we need to authenticate,
#       after sign-in, we should jump to /samples/1
#
#       Store the original requestin the session!

def requires_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect('/signin')

        return f(*args, **kwargs)
    return decorated


def requires_project(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect('/signin')
        if not g.project:
            return redirect('/projects/switch')

        return f(*args, **kwargs)
    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect('/signin')

        if not g.user.is_global_admin:
            if not g.project:
                return redirect('/projects/switch')
            if not g.is_project_admin:
                return redirect('/')

        return f(*args, **kwargs)
    return decorated


@app.route("/")
@requires_project
def index():
    return render_template("index.html")


@app.route("/settings")
@requires_project
def settings():
    return render_template("settings/index.html")


@app.route("/test")
def foo():
    res = ''
    conf.test()
    try:
        cur = g.dbconn.cursor()
        cur.execute("SELECT * FROM users;")
        for record in cur:
            res += str(record)+"<br/>"

        cur.close()
    except Exception, e:
        return "Testing\n<hr/>" + str(e) + "<hr/>" + "Uptime=" + uptime.uptime_str()

    return "Testing\n<hr/>It works!<br/><br/>Users:<br/>" + str(res) + "<hr/>" + "Uptime=" + uptime.uptime_str()


@app.route("/resetdb")
def resetdb():
    conf.initdb()
    return redirect('/')


@app.route("/error")
def error_test():
    raise Exception("Ouch!")


@app.route("/exit")
def exit():
    sys.exit(1)


def run(*args, **kwargs):
    app.run(*args, **kwargs)


#### Import view pages here...

import auth.view
import projects.view
import users.view
import users.edit
if False:
    # no-op to avoid PEP8 warning
    print auth, projects
