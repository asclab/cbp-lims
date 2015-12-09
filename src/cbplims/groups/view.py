from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups

@app.route("/groups/list")
@requires_admin
def list_groups():
    groups = cbplims.groups.avail_groups()
    
    return render_template("groups/list.html",groups=groups )