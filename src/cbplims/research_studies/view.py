from flask import redirect, request, render_template, session, g
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users
import cbplims.diagnoses
import cbplims.research_studies

@app.route("/research_studies/list") 
@requires_user
def list_research_studies():
    research_studies = cbplims.research_studies.list_research_studies()
    return render_template("research_studies/list.html", research_studies = research_studies )


@app.route("/research_studies/<int:rid>/edit" ,methods=['GET', 'POST']) 
@requires_user
def edit_research_studies(rid):
    if request.method == 'GET':
        research_studies = cbplims.research_studies.view_research_studies(rid)
        projects = cbplims.projects.avail_projects()
        return render_template("research_studies/edit.html", research_studies = research_studies, projects=projects )
    else:
        project_id = request.form["project"]
        name = request.form["name"]
        description = request.form["description"]
        date = request.form["date"]
        #return render_template("locations/temp.html", msg= str(name) + " -- " + str(project_id ) )
        msg = cbplims.research_studies.edit_research_studies(rid,project_id,name,description,date)
        research_studies = cbplims.research_studies.list_research_studies()
        return render_template("research_studies/list.html", research_studies = research_studies, msg=msg )
    
@app.route("/research_studies/state", methods=['POST'])
@requires_user
def state_research_studies():
    msg = ''
    if request.method == 'POST':
        research_studies_ids = request.form.getlist("research_studies_id")
    
        if request.form["method"] == "Enable":
            for rid in research_studies_ids:
                msg = cbplims.research_studies.state(rid, 'TRUE')

        if request.form["method"] == "Disable":
            for rid in research_studies_ids:
                msg = cbplims.research_studies.state(rid, 'FALSE') 
        
        research_studies = cbplims.research_studies.list_research_studies()
        return render_template("research_studies/list.html", research_studies = research_studies, msg=msg )
    
@app.route("/research_studies/add" ,methods=['GET', 'POST']) 
@requires_user
def add_research_studies():
     if request.method == 'GET':
         projects = cbplims.projects.avail_projects()
         return render_template("research_studies/add.html", projects=projects )
     else:
         project_id = request.form["project"]
         name = request.form["name"]
         description = request.form["description"]
         date = request.form["date"]
         
         msg = cbplims.research_studies.add_research_studies(project_id,name,description,date)
        
         research_studies = cbplims.research_studies.list_research_studies()
         return render_template("research_studies/list.html", research_studies = research_studies, msg=msg )