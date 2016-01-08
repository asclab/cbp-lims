from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users
import cbplims.diagnoses
import cbplims.sample_types


@app.route("/subjects/list") 
@requires_user
def list_subjects():
    subjects = cbplims.subjects.list_subjects()
    return render_template("subjects/list.html", subjects = subjects )


@app.route("/subjects/add" ,methods=['GET', 'POST']) 
@requires_user
def add_subjects():
     if request.method == 'GET':
         projects = cbplims.projects.avail_projects()
         subject_types = cbplims.subject_types.list_subject_types()
     
         return render_template("subjects/add.html", projects=projects, subject_types=subject_types )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         notes = request.form["notes"]
         subject_types = request.form["subject_types"]
         
         msg = cbplims.subjects.add_subjects(project_id,subject_types,name,notes)
         subjects = cbplims.subjects.list_subjects()
         return render_template("subjects/list.html", msg= msg, subjects=subjects )
     
@app.route("/subjects/state", methods=['POST'])
@requires_user
def state_subjects():
     msg = ''
     if request.method == 'POST':
         subject_ids = request.form.getlist("subjects_id")
         if request.form["method"] == "Enable":
            for sid in subject_ids:
                msg = cbplims.subjects.state(sid, 'TRUE')

         if request.form["method"] == "Disable":
             for sid in subject_ids:
                 msg = cbplims.subjects.state(sid, 'FALSE') 
    
         subjects = cbplims.subjects.list_subjects()
         return render_template("subjects/list.html", msg= msg, subjects=subjects )
     
     
@app.route("/subjects/<int:sid>/view" ,methods=['GET', 'POST']) 
@requires_user
def view_subjects(sid):
     subject = cbplims.subjects.view_subjects(sid)
     diagnoses = cbplims.subjects.view_subjects_diagnoses(sid)
     subject_study = cbplims.subjects.view_subjects_study(sid)
     return render_template("subjects/view.html",  subject=subject, diagnoses=diagnoses, subject_study = subject_study )