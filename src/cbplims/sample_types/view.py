from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users
import cbplims.diagnoses
import cbplims.sample_types

@app.route("/sample_types/list") 
@requires_user
def list_sample_types():
    sample_types = cbplims.sample_types.list_sample_types()
    return render_template("sample_types/list.html", sample_types = sample_types )


@app.route("/sample_types/<int:rid>/edit" ,methods=['GET', 'POST']) 
@requires_user
def edit_sample_types(rid):
    if request.method == 'GET':
        sample_types = cbplims.sample_types.view_sample_types(rid)
        projects = cbplims.projects.get_available_projects(g.user.id)
        return render_template("sample_types/edit.html", sample_types = sample_types, projects=projects )
    else:
        project_id = request.form["project"]
        name = request.form["name"]
        description = request.form["description"]
        date = request.form["date"]
        #return render_template("locations/temp.html", msg= str(name) + " -- " + str(project_id ) )
        msg = cbplims.sample_types.edit_sample_types(rid,project_id,name,description,date)
        sample_types = cbplims.sample_types.list_sample_types()
        return render_template("sample_types/list.html", sample_types = sample_types, msg=msg )
    
@app.route("/sample_types/state", methods=['POST'])
@requires_user
def state_sample_types():
    msg = ''
    if request.method == 'POST':
        sample_types_ids = request.form.getlist("sample_types_id")
    
        if request.form["method"] == "Enable":
            for rid in sample_types_ids:
                msg = cbplims.sample_types.state(rid, 'TRUE')

        if request.form["method"] == "Disable":
            for rid in sample_types_ids:
                msg = cbplims.sample_types.state(rid, 'FALSE') 
        
        sample_types = cbplims.sample_types.list_sample_types()
        return render_template("sample_types/list.html", sample_types = sample_types, msg=msg )
    
@app.route("/sample_types/add" ,methods=['GET', 'POST']) 
@requires_user
def add_sample_types():
     if request.method == 'GET':
         projects = cbplims.projects.avail_projects()
         return render_template("sample_types/add.html", projects=projects )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         description = request.form["description"]
         date = request.form["date"]
         
         msg = cbplims.sample_types.add_sample_types(project_id,name,description,date)
        
         sample_types = cbplims.sample_types.list_sample_types()
         return render_template("sample_types/list.html", sample_types = sample_types, msg=msg )