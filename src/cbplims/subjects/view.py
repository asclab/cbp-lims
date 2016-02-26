from flask import redirect, request, render_template, session, g, make_response
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users
import cbplims.diagnoses
import cbplims.sample_types
import base64

@app.route("/subjects/list") 
@requires_user
def list_subjects():
    subjects = cbplims.subjects.list_subjects()
    return render_template("subjects/list.html", subjects = subjects )


@app.route("/subjects/add" ,methods=['GET', 'POST']) 
@requires_user
def add_subjects():
     if request.method == 'GET':
         projects = cbplims.projects.get_available_projects(g.user.id)
         subject_types = cbplims.subject_types.list_subject_types()
     
         return render_template("subjects/add.html", projects=projects, subject_types=subject_types )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         notes = request.form["notes"]
         subject_types = request.form["subject_types"]
         f = request.form
         files = request.files
         extra = cbplims.subjects.get_extra(f, files, subject_types)
         
         msg = cbplims.subjects.add_subjects(project_id,subject_types,name,notes,extra)
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
     samples = cbplims.samples.view_samples_by_subject_primary(sid)
     
     return render_template("subjects/view.html",  subject=subject, diagnoses=diagnoses, subject_study = subject_study, samples=samples )

@app.route("/subjects/<int:sid>/add_diagnosis" ,methods=['GET', 'POST']) 
@requires_user
def add_diagnosis_subjects(sid):
      if request.method == 'GET':
          subject = cbplims.subjects.view_subjects(sid)
          diagnoses = cbplims.diagnoses.list_diagnoses()
          return render_template("subjects/add_diagnosis.html",  subject=subject, diagnoses=diagnoses )
      else:
          diagnosis = request.form["diagnosis"]
          days_from_primary = request.form["days_from_primary"]
          recorded_date = request.form["recorded_date"]
          is_primary = request.form["is_primary"]
          msg = cbplims.subjects.add_diagnosis(sid,diagnosis,days_from_primary,recorded_date,is_primary)
          return redirect('/subjects/'+str(sid)+'/view')
     

     
@app.route("/subjects/<int:sid>/delete_diagnosis",  methods=['POST'])
@requires_user
def delete_diagnosis_subjects(sid):
      if request.method == "POST":
        msg = '--'
        diagnosis_ids = request.form.getlist("diagnosis_ids")
        if request.form["method"] == "Delete":
            for did in diagnosis_ids:
                cbplims.subjects.delete_diagnosis(sid,did)
      return redirect('/subjects/'+str(sid)+'/view')
     
     
@app.route("/subjects/<int:sid>/add_study" ,methods=['GET', 'POST']) 
@requires_user
def add_subject_study_subjects(sid):
      if request.method == 'GET':
          subject = cbplims.subjects.view_subjects(sid)
          subject_study = cbplims.research_studies.list_research_studies()
          return render_template("subjects/add_subject_study.html",  subject=subject, subject_study=subject_study )
      else:
          subject_study = request.form["subject_study"]
          recorded_date = request.form["recorded_date"]
          msg = cbplims.subjects.add_subject_study(sid,subject_study,recorded_date)
          return redirect('/subjects/'+str(sid)+'/view')

@app.route("/subjects/<int:sid>/delete_study",  methods=['POST'])
@requires_user
def delete_study(sid):
      if request.method == "POST":
        msg = '--'
        study_ids = request.form.getlist("study_ids")
        if request.form["method"] == "Delete":
            for study in study_ids:
                cbplims.subjects.delete_study(sid,study)
      return redirect('/subjects/'+str(sid)+'/view')
     

@app.route("/subjects/<int:sid>/edit" ,methods=['GET', 'POST']) 
@requires_user
def edit_subjects(sid):
     if request.method == 'GET':
         projects = cbplims.projects.get_available_projects(g.user.id)
         subject_types = cbplims.subject_types.list_subject_types()
         
         subject = cbplims.subjects.view_subjects(sid)
         return render_template("subjects/edit.html", subject=subject, projects=projects, subject_types=subject_types )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         notes = request.form["notes"]
         subject_types = request.form["subject_types"]
         f = request.form
         files = request.files
         
         extra = cbplims.subjects.get_extra(f, files, subject_types)
         
         #return render_template("locations/temp.html", msg= str('') + " -- " + str(extra ) )
         
         msg = cbplims.subjects.edit_subjects(project_id,subject_types,name,notes,sid,extra)
         subjects = cbplims.subjects.list_subjects()
         return render_template("subjects/list.html",  subjects=subjects,msg=msg )
        
@app.route("/subjects/<int:sid>/link") 
@requires_user
def make_link(sid):
    subject = cbplims.subjects.view_subjects(sid)
    id = request.args.get('id')
    data = subject.data[id]['base64']
    b64_str = base64.b64decode(data)
    response = make_response(b64_str)
    response.headers["Content-Disposition"] = "attachment; filename=" + str(subject.data[id]['filename'])  
    response.headers["Content-Type"] = subject.data[id]['mime'] 
    #return render_template("locations/temp.html", msg= b64_str )
    return response



