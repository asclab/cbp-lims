from flask import redirect, request, render_template, session
from cbplims import app, requires_user, requires_admin

import cbplims.users
import cbplims.projects

@app.route("/users/view")
@requires_admin 
def users_view():
    users = cbplims.users.get_users()
    return render_template("users/view.html", users=users)
