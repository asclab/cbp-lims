import binascii
import os
import sys

from functools import wraps
from flask import Flask, redirect, render_template, session, g

import config
conf = config.load_config()

import support.uptime
uptime = support.uptime.Uptime()

app = Flask(__name__)
app.secret_key = conf['SECRET_KEY'] if 'SECRET_KEY' in conf else binascii.hexlify(os.urandom(64))


### TODO: make this log to a configured filename
import logging
#import logging.handlers
#file_handler = logging.handlers.RotatingFileHandler(os.path.realpath('../working/cbplims.log'), backupCount=5, maxBytes=1000000)
#file_handler.setLevel(logging.DEBUG)
#app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

import users


# Let's just load a DB connection before each request
@app.before_request
def before_request_wrapper():
    g.uptime = uptime.uptime_str()
    g.dbconn = conf.get_db_conn()


# Be sure to close it
@app.after_request
def after_request_wrapper(response):
    try:
        conf.put_db_conn(g.dbconn)
    except Exception, e:
        print e
    return response


__tmp = app.handle_exception


## even if there is an exception
def handle_exception_wrapper(*args, **kwargs):
    try:
        conf.put_db_conn(g.dbconn)
    except Exception, e:
        print e

    return __tmp(*args, **kwargs)

app.handle_exception = handle_exception_wrapper


def requires_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # TODO: in the case we redirect, setup /signin, and /projects/choose
        #       to redirect back to the original requested page. For example:
        #       if we get a request for /samples/1, and we need to authenticate,
        #       after sign-in, we should jump to /samples/1

        if not 'uid' in session or not session['uid']:
            app.logger.debug("Needs user!")
            return redirect('/signin')

        app.logger.debug("User: <%s> %s", session['uid'], session['username'])

        return f(*args, **kwargs)
    return decorated


def requires_project(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # TODO: in the case we redirect, setup /signin, and /projects/choose
        #       to redirect back to the original requested page. For example:
        #       if we get a request for /samples/1, and we need to authenticate,
        #       after sign-in, we should jump to /samples/1

        if not 'uid' in session or not session['uid']:
            app.logger.debug("Needs user!")
            return redirect('/signin')

        app.logger.debug("User: <%s> %s", session['uid'], session['username'])

        if not 'pid' in session or not session['pid']:
            app.logger.debug("Needs project!")
            return redirect('/projects/switch')
        app.logger.debug("Project: <%s> %s", session['pid'], session['project'])

        return f(*args, **kwargs)
    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not 'uid' in session or not session['uid']:
            return redirect('/signin')

        if not users.is_user_global_admin(session['uid']):
            if not 'pid' in session or not session['pid']:
                return redirect('/projects/choose')

            # TODO: check to see if the user is a project_admin
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
if False:
    # no-op to avoid PEP8 warning
    print auth, projects
