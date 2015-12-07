from flask import render_template, request, session, g, redirect
from cbplims import app, requires_admin, requires_user

import cbplims.users
import cbplims.projects

@app.route("/settings/global/user_add",  methods=['GET', 'POST'])
@requires_admin
def users_add():
    if request.method == "GET":
        projects = cbplims.projects.get_available_projects(g.user.id)
        return render_template("settings/users/add.html", projects=projects)
    elif request.method == "POST":
        full_name = request.form['full_name']
        username = request.form['username']
        
        is_admin = request.form.getlist('is_admin')
        if not is_admin:
            is_admin.append("False")
        pwd = request.form['pwd']
        pwd=cbplims.users.add_user(full_name,username,is_admin[0],pwd)
        return render_template("settings/users/add.html", username=username)


@app.route("/settings/global/users/<int:pid>/delete" , methods=['POST'])
@requires_admin
def users_del(pid):
    if request.method == "POST":
        go = cbplims.users.del_user(pid)
        # put into logger, return false will go to erro page. 
    return redirect('./settings/global/users')

@app.route("/settings/global/<int:pid>/user_edit" , methods=['GET','POST'])
@requires_user
def users_edit(pid):
    if request.method == "GET":
        info = cbplims.users.get_user(pid)
        # put into logger, return false will go to erro page.
    elif request.method == "POST":
        full_name = request.form['full_name']
        username = request.form['username']
        is_admin = request.form.getlist('is_admin')
        if not is_admin:
            is_admin.append("False")
        #pwd_n = request.form['pwd_n']
        #pwd_o=request.form['pwd_o']
        ## needs to add a check that admin does not need to match old pwd with new 
        #pwd=cbplims.users.add_user(full_name,username,is_admin[0],pwd_n)
        return redirect('./settings/global/users')
    return render_template("settings/users/edit.html", info=info)

