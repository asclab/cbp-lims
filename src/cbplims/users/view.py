from flask import render_template, request, g, redirect
from cbplims import app, requires_admin, requires_user

import cbplims.users
import cbplims.projects
import cbplims.groups

@app.route("/settings/global/users", methods=['GET', 'POST'])
@requires_admin
def users_list():
    msg = []
    if request.method == 'POST':
        app.logger.debug("Users form method: %s", request.form["method"])

        user_ids = request.form.getlist("user_id")

        if request.form["method"] == "Delete":
            app.logger.debug("Deleting user_id(s): %s", ','.join(user_ids))
            for uid in user_ids:
                if int(uid) == g.user.id:
                    msg.append("You can't delete yourself!")
                    continue
                cbplims.users.del_user(uid)

        elif request.form["method"] == "Disable":
            app.logger.debug("Disabling user_id(s): %s", ','.join(user_ids))
            for uid in user_ids:
                if int(uid) == g.user.id:
                    msg.append("You can't disable yourself!")
                    continue
                cbplims.users.disable_user(uid)

        elif request.form["method"] == "Enable":
            app.logger.debug("Enabling user_id(s): %s", ','.join(user_ids))
            for uid in user_ids:
                cbplims.users.enable_user(uid)

    users = cbplims.users.get_users()
    return render_template("settings/users/list.html", users=users, msg=msg)


@app.route("/settings/global/users/add",  methods=['GET', 'POST'])
@requires_admin
def users_add():
    if request.method == "GET":
        return render_template("settings/users/add.html", user=None)

    elif request.method == "POST":
        # TODO: check password match
        fullname = request.form['fullname']
        username = request.form['username']
        is_admin = request.form.getlist('is_admin')
        allow_password_change = request.form.getlist('allow_password_change')

        password = request.form['password']
        cbplims.users.add_user(fullname, username, password, True if is_admin else False, True if allow_password_change else False)

        return redirect('/settings/global/users')


@app.route("/settings/profile")
@requires_user
def users_profile_view():
    groups = cbplims.groups.get_user_group(g.user.id)
    return render_template("settings/users/view.html", user=g.user, profile=True, groups=groups)


@app.route("/settings/profile/edit", methods=['GET', 'POST'])
@requires_user
def users_profile_edit():
    if request.method == "GET":
        return render_template("settings/users/add.html", user=g.user, profile=True)
        # put into logger, return false will go to erro page.

    elif request.method == "POST":
        # TODO: check password match
        fullname = request.form['fullname']

        cbplims.users.edit_user(g.user.id, fullname, request.form["password"])

        return redirect('/settings/profile')


@app.route("/settings/global/users/<int:uid>")
@requires_admin
def users_view(uid):
    user = cbplims.users.get_user(uid)
    return render_template("settings/users/view.html", user=user)


@app.route("/settings/global/users/<int:uid>/edit", methods=['GET', 'POST'])
@requires_admin
def users_edit(uid):
    if request.method == "GET":
        user = cbplims.users.get_user(uid)
        return render_template("settings/users/add.html", user=user)
        # put into logger, return false will go to erro page.

    elif request.method == "POST":
        # TODO: check password match
        fullname = request.form['fullname']
        is_admin = request.form.getlist('is_admin')
        allow_password_change = request.form.getlist('allow_password_change')

        app.logger.debug("userid:%s, fullname:%s, is_admin:%s, allow_password_change:%s", uid, fullname, is_admin, allow_password_change)
        cbplims.users.edit_user(uid, fullname, request.form["password"], True if is_admin else False, True if allow_password_change else False)

        return redirect('/settings/global/users')
