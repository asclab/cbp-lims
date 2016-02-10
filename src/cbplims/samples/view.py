from flask import redirect, request, render_template, session, g, jsonify
from cbplims import app, requires_user, requires_admin

import cbplims.groups
import cbplims.projects
import cbplims.users
import cbplims.diagnoses
import cbplims.sample_types
import cbplims.subjects
import cbplims.location

@app.route("/samples/add" , methods=['GET', 'POST']) 
@requires_user
def list_samples():
    if request.method == 'GET':
        subjects = cbplims.subjects.list_subjects()
        sample_types = cbplims.sample_types.list_sample_types()
        location_storable = cbplims.location.list_location_storable()
        return render_template("samples/add.html", subjects = subjects, sample_types = sample_types, location_storable=location_storable )
    else:
        locations = request.form.getlist("location_use")
        parent_location_selected = request.form["parent_location_selected"]
        sampletype_id = request.form["sample_type"]
        sampletype_name = request.form["sample_type_name"]
        subject = request.form["subject"]
        notes = request.form["notes"]
        date = request.form["datec"]
        subject = subject.split(",")
        subject= subject[0]
        sample_ids = request.form.getlist("sample_id")
        # get extra information 
        f = request.form
        files = request.files
        extra = cbplims.subjects.get_extra(f, files, sampletype_id)
        
        return render_template("locations/temp.html", msg= str(sample_ids) +  ":<hr>:" + str(f)   )
        # multiple locations are allow
        # for each location a new entry will be submitted
        # a new name for the sample will be created automatically
        # subject#_sample#_tissue_type
        
        ##
        barcode,name = cbplims.samples.add_sample(sampletype_name,sampletype_id,subject,date,notes,locations,parent_location_selected,extra)
        return render_template("locations/temp.html", msg= str(barcode) +  "::" + str(name)   )
#

@app.route("/samples/get_child_samples" , methods=["GET"])
@requires_user
def get_child_samples():
     subject = request.args.get('subject')
     #start = subject.find('id:')+3
     #end = subject.find(' n',start)
     # write a function to get all child samples here and return it. 
     
     return jsonify(result=[subject,'test'])
    

@app.route("/samples/get_location_matrix" , methods=["GET"])
@requires_user
def get_location_matrix():
     lid = request.args.get('location')
     dim = cbplims.location.dim_location(lid)
     locations = cbplims.location.child_location_simple(lid)
     return jsonify(dim=dim,is_used=locations)
    