import os
import sys
import json
import atexit
import logging
import binascii
import threading

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

    def close_dblogger():
        dblogger.close()

    atexit.register(close_dblogger)

except:
    dblogger = None
    sys.stderr.write("Unable to setup DB Logger!\n")


import users

app.logger.debug("Starting up Flask app")


# Let's just load a DB connection before each request
@app.before_request
def before_request_wrapper():
    if request.path in ['/resetdb', '/restart']:
        return

    if not request.path in ['/log', '/dbconsole']:
        if not request.path[:7] == '/static':
            app.logger.debug(request.method+" "+request.path)

    g.uptime = uptime.uptime_str()
    g.dbconn = conf.get_db_conn()
    g.debug = True if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'dev' else False

    g.is_project_admin = False
    g.is_project_view = False
    g.user = None
    g.project = None

    if 'uid' in session and session['uid']:
        g.user = users.get_user(session['uid'])
        g.allow_switch_project = True
        if not g.user.is_global_admin:
            avail = projects.get_available_projects(g.user.id)
            if len(avail) == 1:
                g.allow_switch_project = False

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
        app.logger.error(err)
        print "Error: %s " % err

    try:
        if g.dbconn:
            conf.put_db_conn(g.dbconn)
    except Exception, e:
        app.logger.error(e)
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


def requires_global_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect('/signin')

        if not g.user.is_global_admin:
            return redirect('/')

        return f(*args, **kwargs)
    return decorated


@app.route("/")
@requires_project
def index():
    return render_template("index.html")


@app.route("/settings/")
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
    app.logger.info("Reloading DB at user request")

    global dblogger
    if dblogger:
        dblogger.close()
        app.logger.removeHandler(dblogger)

        dblogger = support.dblogger.DBLogger(conf.build_db_conn())
        app.logger.addHandler(dblogger)

    conf.initdb()
    return redirect('/')


@app.route("/log")
@requires_admin
def view_dblogger():
    if not dblogger:
        return "Log not available"

    # app.logger.debug(str(request.args))

    def json_str(obj):
        print "Serializing: %s" % obj
        return str(obj)

    if 'last' in request.args:
        try:
            messages = dblogger.fetch_messages(int(request.args['last']))
            s = json.dumps([x._asdict() for x in messages], default=json_str)
            return s
        except Exception, e:
            print e
            return e
    else:
        messages = dblogger.fetch_messages()
        return render_template('dblogger.html', messages=messages)


@app.route("/dbconsole", methods=['GET', 'POST'])
@requires_global_admin
def dbconsole():
    if request.method == "GET":
        return render_template("dbconsole.html", records=[])

    elif request.method == "POST":
        query = request.form["query"].strip()
        records = []
        names = []
        msg = ""

        if query:
            app.logger.debug("SQL: %s", query)

            try:
                cur = g.dbconn.cursor()
                cur.execute(query)

                if cur.rowcount == 1:
                    msg = "1 record"
                else:
                    msg = "%s records" % cur.rowcount

                if query.upper()[:6] == "SELECT":
                    records = list(cur.fetchall())
                    names = [x[0] for x in cur.description]
                else:
                    g.dbconn.commit()

            except Exception, e:
                app.logger.error(e)
                msg = str(e)

            cur.close()

        return render_template('dbconsole.html', records=records, names=names, query=query, msg=msg)


@app.route("/restart")
def restart_app():
    app.logger.info("Restarting app at user request")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return render_template('restart.html')


def run(*args, **kwargs):
    app.run(*args, **kwargs)


#### Import view pages here...

import auth.view
import projects.view
import users.view
import groups.view
import location.view
if False:
    # no-op to avoid PEP8 warning
    print auth, projects
