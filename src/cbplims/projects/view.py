from flask import redirect, request, render_template, session, g
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

    return redirect('/')


@app.route("/projects/switch")
@requires_user
def switch_project():
    avail = cbplims.projects.get_available_projects(g.user.id)
    return render_template("projects/switch.html", projects=avail)


@app.route("/projects/new",  methods=['GET', 'POST'])
@requires_admin
def new_project():
    if request.method == "GET":
        return render_template("projects/new.html")

    pid = cbplims.projects.new_project(request.form['name'], g.project.id if g.project else None, g.user.id)
    app.logger.debug("New project: %s", pid)
    return redirect('/')
