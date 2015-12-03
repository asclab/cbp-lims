from flask import render_template
from cbplims import app, requires_admin

import cbplims.users
import cbplims.projects


@app.route("/settings/global/users")
@requires_admin
def users_view():
    users = cbplims.users.get_users()
    return render_template("settings/users/view.html", users=users)
