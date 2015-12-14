from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.users
import cbplims.projects


@app.route("/projects/switch", methods=['GET', 'POST'])
@requires_user
def switch_project():
    if request.method == "GET":
        avail = cbplims.projects.get_available_projects(g.user.id)

        if len(avail) == 1 and not g.user.is_global_admin:
            app.logger.debug("Auto-selected only project: %s", avail[0])
            session['pid'] = avail[0].id
            return redirect('/')

        return render_template("projects/switch.html", projects=avail)

    project = cbplims.projects.get_project(request.form['project_id'])
    app.logger.debug('selected project: %s => %s', request.form['project_id'], project)

    if project:
        session['pid'] = project.id
    return redirect('/')


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
        return render_template("projects/add.html", parents=avail)
    elif request.method == "POST":
        project_name = request.form['project_name']
        parent = request.form['parent']
        project_code = request.form['project_code']
        msg = cbplims.projects.new_project(project_name, project_code, parent)
        avail = cbplims.projects.avail_projects()
        return render_template("projects/add.html", parents=avail, msg=msg)
    return redirect('/')


@app.route("/projects/list")
@requires_admin
def list_project():
    if request.method == "GET":
        avail = cbplims.projects.get_projects_recursive()
        return render_template("projects/list.html", parents=avail)
    return redirect('/')


@app.route("/projects/<int:pid>/promote",  methods=['POST'])
@requires_admin
def promote_project(pid):
    if request.method == "POST":
        new_id = request.form['id']
        cbplims.projects.promote_projects_child(pid, new_id)
        return redirect('projects/list')


@app.route("/projects/state",  methods=['POST'])
@requires_admin
def changeState():
    if request.method == "POST":
        msg = '--'
        project_ids = request.form.getlist("project_ids")
        if request.form["method"] == "Enable":
            for pid in project_ids:
                msg = cbplims.projects.change_state_project(pid, 'TRUE')
        
        if request.form["method"] == "Disable":
            for pid in project_ids:
                msg = cbplims.projects.change_state_project(pid, 'FALSE')
                
        #
        avail = cbplims.projects.get_projects_recursive()
        return render_template("projects/list.html", parents=avail, msg=msg)


@app.route("/projects/<int:pid>/edit",  methods=['GET', 'POST'])
@requires_admin
def edit_project(pid):
    
    if request.method == "GET":
        project_name = request.args.get('name')
        project_code = request.args.get('code')
        return render_template("projects/edit.html", project_name=project_name, project_id=pid, project_code=project_code)
    else:
        project_name = request.form['name']
        project_code = request.form['code']
        msg = cbplims.projects.update_projects(pid, project_name, project_code)
        avail = cbplims.projects.get_projects_recursive()
        return render_template("projects/list.html", parents=avail, msg=msg)
