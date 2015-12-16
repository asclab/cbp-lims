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
    return render_template("locations/list.html",locations=locations, dim=dim )


@app.route("/location/<int:pid>/matrix")
@requires_user
def matrix_location(pid):
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
        
        
        route = "/location/"+str(request.form["parent_id"])+"/list"
        return redirect(route)





    
@app.route("/location/<int:id>/add",methods=['GET', 'POST']) 
@requires_user
def add_location(id):
    if request.method == 'GET':
        location = cbplims.location.view_location(id)
        projects = cbplims.projects.avail_projects()
        return render_template("locations/add.html",projects=projects,location=location )