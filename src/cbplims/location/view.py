from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users

@app.route("/location/<int:pid>/list") 
@requires_user
def list_location(pid):
    locations = cbplims.location.child_location(pid)
    return render_template("locations/list.html",locations=locations )