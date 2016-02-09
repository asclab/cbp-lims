from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users

@app.route("/location/<int:pid>/list") 
@requires_user
def list_location(pid):
    # get id of top_tier project 
    top_project_id = cbplims.projects.get_top_project_id(g.project.id)
    locations = cbplims.location.child_location(pid, top_project_id)
    return render_template("locations/list.html",locations=locations,back=pid)

@app.route("/location/<int:pid>/list_back") 
@requires_user
def list_location_back(pid):
    top_project_id = cbplims.projects.get_top_project_id(g.project.id)
    if pid == 1:
        locations = cbplims.location.child_location(0,top_project_id)
        return render_template("locations/list.html",locations=locations)
    pid = cbplims.location.get_grand(pid)
    locations = cbplims.location.child_location(pid,top_project_id)
    return render_template("locations/list.html",locations=locations,  )


@app.route("/location/<int:pid>/matrix")
@requires_user
def matrix_location(pid):
    dim = cbplims.location.dim_location(pid)
    top_project_id = cbplims.projects.get_top_project_id(g.project.id)
    locations = cbplims.location.child_location_simple(pid)
    #return render_template("locations/temp.html", msg=str(top_project_id) + " :: " + str(pid) + " :: " + str(locations) )
    return render_template("locations/list_table.html",locations=locations,dim=dim,back=pid )





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
        
        parent_id = request.form["parent_id"]
        if parent_id == "None":
            parent_id = 0
        route = "/location/"+str(parent_id)+"/list"
        return redirect(route)





    
@app.route("/location/<int:id>/add",methods=['GET', 'POST']) 
@requires_user
def add_location(id):
    if request.method == 'GET':
        location = cbplims.location.view_location(id)
        # projects that are listed will contain all projects under the top_tier project
        projects = cbplims.projects.view_toptier(g.project.id)
        if request.args.get('row') >0 or request.args.get('col') > 0:
            in_row = request.args.get('row')
            in_col = request.args.get('col')
        else:
            in_row = 'None'
            in_col = 'None'
        
        return render_template("locations/add.html",projects=projects,location=location,in_row=in_row,in_col=in_col )
    else:
        in_row = request.form["in_row"]
        in_col = request.form["in_col"]
        project_id = request.form["project"]
        my_row = request.form["row"]
        my_col = request.form["col"]
        location_name = request.form["location_name"]
        is_primary = request.form["is_primary"]
        is_storable = request.form["is_storable"]
        notes = request.form["notes"]
        
        
        # add to location directly
        if (is_primary == "yes"):
            id = None
        # now add to location_project
        
        msg = cbplims.location.add_location(id,in_row,in_col,my_row,my_col,location_name,notes,project_id,is_storable)
        #return render_template("locations/temp.html", msg=str(msg) + " :: " + str(is_storable)   )
        if in_row >0 or in_col > 0:
            route = "/location/"+str(id)+"/matrix"
        else:
            route = "/location/"+str(id)+"/list"
        return redirect(route) 
        #return render_template("locations/temp.html", msg=msg )
        
        
@app.route("/location/<int:id>/edit",methods=['GET', 'POST']) 
@requires_user
def edit_location(id):
    if request.method == 'GET':
        location = cbplims.location.view_location(id)
        projects = cbplims.projects.avail_projects()
        return render_template("locations/edit.html",msg='hi' + str(id), location=location,projects=projects)
    else:
        project_id = request.form["project"]
        my_row = request.form["row"]
        my_col = request.form["col"]
        location_name = request.form["location_name"]
        notes = request.form["notes"]
        is_storable = request.form["is_storable"]
        msg = cbplims.location.edit_location(id,project_id,my_row,my_col,location_name,notes,is_storable)
        location = cbplims.location.view_location(id)
        route = "/location/"+str(location.parent_id)+"/list"
        return redirect(route) 
        #return render_template("locations/temp.html", msg=msg )