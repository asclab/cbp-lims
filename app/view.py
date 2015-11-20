#!flask/bin/python
from app import app
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import escape
import pickle
from flask import jsonify
from urlparse import urlparse, urljoin
from flask.ext.wtf import Form


# database access
import psycopg2
# login manager
from flask.ext.login import LoginManager
import json


# connect to postgres
with open('./app/db.pickle') as f:
    pwd = pickle.load(f)
conn = psycopg2.connect(pwd[0])
################################################################################
### General properties
### every route will first check for session login else its going to redirect to login.html
### templates always include {{name}} (login email) if not the template will only produce a link to login
### {{msg}} this is a generic tag that is used to output any generic message and is build into every route.
### html rendered is always the same name as the route.  Example: search_sample will have a corresponding search_sample.html
### names are not grammatically correct and ending is "s" is avoided when possible.

# this route will is for viewing ALL subjects. 



@app.route('/view_subject', methods=['GET', 'POST'])
def view_subject():
    
    if 'username' in session:
        cur = conn.cursor()
        action = request.args.get("action" , type=int )
        num_row_start = request.args.get("numrows", type=int )
        limit = 10
        if num_row_start is None:
            num_row_start = 0
        num_row_end = num_row_start+ limit  
        

        final =[]

        try: 
            cur.execute('BEGIN WORK;')
            getid = 'SELECT id, users, age, sex, date_collection, timestamp, notes FROM subject ORDER BY id DESC LIMIT %s OFFSET %s ;'
            cur.execute(getid, (limit,num_row_start))
            rows = cur.fetchall()
            # now loop through each id and get from three tables: projects, consent, diagnosis,
           
            for sID in rows:
                pre =[] 
                pre.append(sID)
                tempid = sID[0]
                
                mconsent = ('SELECT consent.form, consent.notes FROM subject '
                            'INNER JOIN subject_consent '
                             'ON subject_consent.subject_id = subject.id '
                             'AND subject_consent.subject_id = %s '
                             ' INNER JOIN consent'
                             ' ON consent.id = subject_consent.consent_id'
                )
                
                cur.execute(mconsent, (tempid,))
                crows = cur.fetchall()
                pre.append(crows)
                
                mprojects = ('SELECT projects.name, projects.groupname, projects.notes FROM subject '
                                'INNER JOIN subject_project ' 
                                'ON subject_project.subject_id = subject.id ' 
                                'AND subject_project.subject_id = %s '
                                'INNER JOIN projects '
                                'ON projects.id = subject_project.project_id'
                )

                cur.execute(mprojects, (tempid,))
                prows = cur.fetchall()
                pre.append(prows)
                
                mdiagnosis = ('SELECT diagnosis.disease, diagnosis.notes FROM subject '
                                 'INNER JOIN subject_diagnosis ' 
                                 'ON subject_diagnosis.subject_id = subject.id ' 
                                 'AND subject_diagnosis.subject_id = %s '
                                 'INNER JOIN diagnosis '
                                 'ON diagnosis.id = subject_diagnosis.diagnosis_id '
                )
                 
                cur.execute(mdiagnosis, (tempid,))
                drows = cur.fetchall()

                cur.execute('COMMIT WORK;')
                
                pre.append(drows)
                final.append(pre)

        except Exception as err:
            conn.rollback() 
            return render_template("error.html",error="there was an error!: " + str(err),name=escape(session['username'])   )
            
        return render_template("view_subject.html",final=final,name=escape(session['username']), next=num_row_end )
        
    return redirect(url_for('login'))
