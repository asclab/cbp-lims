from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin


import cbplims.projects
import cbplims.subject_types
import cbplims.sample_types

@app.route("/subject_types/list") 
@requires_user
def list_subject_types():
    subject_types = cbplims.subject_types.list_subject_types()
    return render_template("subject_types/list.html", subject_types = subject_types )

@app.route("/subject_types/<int:sid>/edit" ,methods=['GET', 'POST']) 
@requires_user
def edit_subject_types(sid):
    if request.method == 'GET':
        subject_types = cbplims.subject_types.view_subject_types(sid)
        projects = cbplims.projects.get_available_projects(g.user.id)
        return render_template("subject_types/edit.html", subject_types = subject_types, projects=projects )
    else:
        project_id = request.form["project"]
        name = request.form["name"]
        description = request.form["description"]
        f = request.form
        extra = cbplims.sample_types.get_extra(f)
        
        #return render_template("locations/temp.html", msg= str(name) + " -- " + str(extra ) )
        msg = cbplims.subject_types.edit_subject_types(sid,project_id,name,description,extra)
        subject_types = cbplims.subject_types.list_subject_types()
        return render_template("subject_types/list.html", subject_types = subject_types, msg=msg )
    
@app.route("/subject_types/state", methods=['POST'])
@requires_user
def state_subject_types():
     msg = ''
     if request.method == 'POST':
         subject_types_ids = request.form.getlist("subject_types_id")
         if request.form["method"] == "Enable":
            for sid in subject_types_ids:
                msg = cbplims.subject_types.state(sid, 'TRUE')

         if request.form["method"] == "Disable":
             for sid in subject_types_ids:
                 msg = cbplims.subject_types.state(sid, 'FALSE') 
    
         subject_types = cbplims.subject_types.list_subject_types()
         return render_template("subject_types/list.html", subject_types = subject_types, msg=msg )
        

@app.route("/subject_types/add" ,methods=['GET', 'POST']) 
@requires_user
def add_subject_types():
     if request.method == 'GET':
         projects = cbplims.projects.avail_projects()
         return render_template("subject_types/add.html", projects=projects )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         fields = request.form["fields"]
         
         
         msg = cbplims.subject_types.add_subject_types(project_id,name,fields)
        
         subject_types = cbplims.subject_types.list_subject_types()
         return render_template("subject_types/list.html", subject_types = subject_types, msg=msg )