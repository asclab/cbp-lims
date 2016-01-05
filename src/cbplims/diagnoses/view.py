from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users
import cbplims.diagnoses

@app.route("/diagnoses/list") 
@requires_user
def list_diagnoses():
    diagnoses = cbplims.diagnoses.list_diagnoses()
    return render_template("diagnoses/list.html", diagnoses = diagnoses )


@app.route("/diagnosis/<int:did>/edit" ,methods=['GET', 'POST']) 
@requires_user
def edit_diagnoses(did):
    if request.method == 'GET':
        diagnosis = cbplims.diagnoses.view_diagnosis(did)
        projects = cbplims.projects.avail_projects()
        return render_template("diagnoses/edit.html", diagnosis = diagnosis, projects=projects )
    else:
        project_id = request.form["project"]
        name = request.form["name"]
        #return render_template("locations/temp.html", msg= str(name) + " -- " + str(project_id ) )
        msg = cbplims.diagnoses.edit_diagnosis(did,project_id,name)
        diagnoses = cbplims.diagnoses.list_diagnoses()
        return render_template("diagnoses/list.html", msg = msg, diagnoses = diagnoses )
    
    
@app.route("/diagnoses/state", methods=['POST'])
@requires_user
def state_diagnoses():
    msg = ''
    if request.method == 'POST':
        diagnoses_ids = request.form.getlist("diagnosis_id")
    
        if request.form["method"] == "Enable":
            for did in diagnoses_ids:
                msg = cbplims.diagnoses.state(did, 'TRUE')

        if request.form["method"] == "Disable":
            for did in diagnoses_ids:
                msg = cbplims.diagnoses.state(did, 'FALSE') 
        
        diagnoses = cbplims.diagnoses.list_diagnoses()
        return render_template("diagnoses/list.html", msg = msg, diagnoses = diagnoses )
    
    
@app.route("/diagnosis/add" ,methods=['GET', 'POST']) 
@requires_user
def add_diagnoses():
     if request.method == 'GET':
         projects = cbplims.projects.avail_projects()
         return render_template("diagnoses/add.html", projects=projects )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         #return render_template("locations/temp.html", msg= str(name) + " -- " + str(project_id ) )
         msg = cbplims.diagnoses.add_diagnosis(project_id,name)
         projects = cbplims.projects.avail_projects()
         
         diagnoses = cbplims.diagnoses.list_diagnoses()
         return render_template("diagnoses/list.html", msg = msg, diagnoses = diagnoses )