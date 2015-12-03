from flask import redirect, request, render_template, session, g
from cbplims import app

import cbplims.auth


@app.route("/signout")
def signout():
    session.pop('uid', None)
    session.pop('pid', None)
    g.user = None
    g.project = None
    return render_template("signout.html")


@app.route("/signin",  methods=['GET', 'POST'])
def signin():
    if request.method == "GET":
        return render_template("signin.html")

    userid = cbplims.auth.authenticate(request.form['username'], request.form['password'])

    if userid:
        session['uid'] = userid

        app.logger.debug('USER LOGIN: <%s> %s', session['uid'], request.form['username'])

        return redirect('/')

    else:
        error = 'Invalid username/password'
        return render_template("signin.html", error=error)
