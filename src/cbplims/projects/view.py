from flask import redirect, request, render_template, session
from cbplims import app, requires_user, requires_admin

import cbplims.users
import cbplims.projects


@app.route("/projects/<int:pid>/select")
@requires_user
def select_project(pid):
    project = cbplims.projects.get_project(pid)
    app.logger.debug('selected project: %s => %s', pid, project)

    if project:
        session['pid'] = pid
        session['project'] = project.name

    return redirect('/')


@app.route("/projects/switch")
@requires_user
def switch_project():
    print session['uid']

    uid = session['uid']
    app.logger.debug('userid: %s', uid)
    avail = cbplims.projects.get_available_projects(uid)
    admin = cbplims.users.is_user_global_admin(uid)

    return render_template("projects/switch.html", projects=avail, admin=admin)


@app.route("/projects/new",  methods=['GET', 'POST'])
@requires_admin
def new_project():
    if request.method == "GET":
        return render_template("projects/new.html")

    pid = cbplims.projects.new_project(request.form['name'], session['pid'] if 'pid' in session else None, session['uid'])
    app.logger.debug("New project: %s", pid)
    return redirect('/')


