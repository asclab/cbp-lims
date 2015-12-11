from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users

@app.route("/groups/list")
@requires_admin
def list_groups():
    groups = cbplims.groups.avail_groups()
    return render_template("groups/list.html",groups=groups )


@app.route("/groups/add",methods=['GET', 'POST'])
@requires_admin
def add_groups():
    if request.method == "GET":
        groups = cbplims.groups.avail_alluser()
        projects = cbplims.projects.avail_projects()
        users = cbplims.users.get_users()
        return render_template("groups/add.html",groups=groups, projects=projects )
    elif request.method == "POST":
        project = request.form.getlist('project')
        role = request.form.getlist('role')
        msg = cbplims.groups.add_groups(project[0],role[0])
        groups = cbplims.groups.avail_alluser()
        projects = cbplims.projects.avail_projects()
        users = cbplims.users.get_users()
        return render_template("groups/add.html",groups=groups, projects=projects, msg=msg )

@app.route("/groups/user_group",methods=['GET', 'POST'])
@requires_admin
def user_group():
    if request.method == "GET":
        groups = cbplims.groups.avail_groups()
        projects = cbplims.projects.avail_projects()
        users = cbplims.users.get_users()
        return render_template("groups/user_group.html",groups=groups, projects=projects, users=users )
    elif request.method == "POST":
        user = request.form.getlist('user')
        project_add = request.form.getlist('add')
        msg = cbplims.groups.add_user_groups(user[0],project_add[0])
        groups = cbplims.groups.avail_groups()
        projects = cbplims.projects.avail_projects()
        users = cbplims.users.get_users()
        return render_template("groups/user_group.html",groups=groups, projects=projects, users=users, msg=msg )


@app.route("/groups/<int:pid>/view")
@requires_user
def view_groups(pid):
    groups = cbplims.groups.get_groups(pid)
    return render_template("groups/view.html",groups=groups )