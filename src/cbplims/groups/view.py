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
    groups = cbplims.groups.view_groups(pid)
    return render_template("groups/view.html",groups=groups )


@app.route("/groups/state", methods=['POST'])
@requires_admin
def state_groups():
    msg = ''
    if request.method == 'POST':
        group_ids = request.form.getlist("group_id")
    
        if request.form["method"] == "Enable":
            for gid in group_ids:
                msg = cbplims.groups.change_state_group(gid,'TRUE')

        if request.form["method"] == "Disable":
            for gid in group_ids:
                msg = cbplims.groups.change_state_group(gid,'FALSE') 
        
        groups = cbplims.groups.avail_groups()
        return render_template("groups/list.html", groups=groups, msg=msg )
    
@app.route("/groups/<int:gid>/edit",  methods=['GET', 'POST'])
@requires_admin
def edit_group(gid):
    msg = ''
    if request.method == "GET":
        group = cbplims.groups.view_groups(gid)
        return render_template("groups/edit.html", group=group[0])
    else:
        group_name = request.form['name']
        group_role = request.form['role']
        msg = cbplims.groups.edit_group(gid,group_name,group_role)
        groups = cbplims.groups.avail_groups()
        return render_template("groups/list.html", groups=groups, msg=msg )