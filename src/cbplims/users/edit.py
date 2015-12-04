from flask import render_template, request, session, g
from cbplims import app, requires_admin

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
        email = request.form['email']
        is_admin = request.form.getlist('is_admin')
        if not is_admin:
            is_admin.append("False")
        pwd = request.form['pwd']
        pwd=cbplims.users.add_user(full_name,username,email,is_admin[0],pwd)
        return render_template("settings/users/add.html", username=username)
