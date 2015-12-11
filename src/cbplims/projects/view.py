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

@app.route("/projects/<int:pid>/view")
@requires_user
def view_project(pid):
    info = cbplims.projects.view_project(pid)
    groups = cbplims.groups.get_specific_group(pid)
    return render_template("projects/view.html", info=info, groups=groups)


@app.route("/projects/new",  methods=['GET', 'POST'])
@requires_admin
def new_project():
    if request.method == "GET":
        return render_template("projects/new.html")

    pid = cbplims.projects.new_project(request.form['name'], g.project.id if g.project else None, g.user.id)
    app.logger.debug("New project: %s", pid)
    return redirect('/')


@app.route("/projects/add",  methods=['GET', 'POST'])
@requires_admin
def add_project():
    if request.method == "GET":
        avail = cbplims.projects.avail_projects()
        return render_template("projects/add.html",parents=avail)
    elif request.method == "POST":
        project_name = request.form['project_name']
        parent = request.form['parent']
        project_code = request.form['project_code']
        msg =cbplims.projects.new_project(project_name,project_code, parent)
        avail = cbplims.projects.avail_projects()
        return render_template("projects/add.html",parents=avail,msg=msg)
    return redirect('/')

@app.route("/projects/list")
@requires_admin
def list_project():
    if request.method == "GET":
        avail = cbplims.projects.get_projects_recursive()
        return render_template("projects/list.html",parents=avail)
    return redirect('/')

@app.route("/projects/<int:pid>/promote",  methods=['POST'])
@requires_admin
def promote_project(pid):
    if request.method == "POST":
        id = request.form['id']
        msg = cbplims.projects.promote_projects_child(pid,id)
        return redirect('projects/list')

@app.route("/projects/<int:pid>/changeState",  methods=['POST'])
@requires_admin
def changeState(pid):
    if request.method == "POST":
        state = request.form['state']
        msg = cbplims.projects.change_state_project(pid,state)
        return redirect('projects/list')


@app.route("/projects/<int:pid>/edit",  methods=['GET', 'POST'])
@requires_admin
def edit_project(pid):
    if request.method == "POST":
        project_name = request.form['name']
        project_code = request.form['code']
        do = request.form['do']
        if int(do)== 0:
            #msg = "hi: " + str(project_code) + " " + str(project_name) + " " + str(pid)
            return render_template("projects/edit.html",project_name=project_name, project_id=pid, project_code=project_code)
        else:
            msg = cbplims.projects.update_projects(pid,project_name,project_code)
            avail = cbplims.projects.get_projects_recursive()
            return render_template("projects/list.html",parents=avail, msg=msg)