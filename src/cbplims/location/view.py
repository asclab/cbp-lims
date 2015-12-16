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



@app.route("/location/state", methods=['POST'])
@requires_user
def state_locations():
    msg = ''
    if request.method == 'POST':
        location_ids = request.form.getlist("location_id")
    
        if request.form["method"] == "Enable":
            for lid in location_ids:
                msg = cbplims.location.change_state_location(lid, 'TRUE')

        if request.form["method"] == "Disable":
            for lid in location_ids:
                msg = cbplims.location.change_state_location(lid, 'FALSE') 
        
        
        locations = cbplims.location.child_location(request.form["parent_id"])
        return render_template("locations/list.html",locations=locations,msg=msg )