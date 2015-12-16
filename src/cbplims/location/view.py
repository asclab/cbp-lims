from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users

@app.route("/location/<int:pid>/list") 
@requires_user
def list_location(pid):
    dim = cbplims.location.dim_location(pid)
    locations = cbplims.location.child_location(pid)
    if dim.row == 0 & dim.col ==0:
        return render_template("locations/list.html",locations=locations )
    else:
        return render_template("locations/list_table.html",locations=locations,dim=dim )



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
    
    
@app.route("/location/<int:id>/add",methods=['GET', 'POST']) 
@requires_user
def add_location(id):
    if request.method == 'GET':
        # two different types of add
        # matrix or single depending on if my_row or my_col > 0 
        locations = cbplims.location.child_location(id)
        return render_template("locations/list.html",locations=locations )