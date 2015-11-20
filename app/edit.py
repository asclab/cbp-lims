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

# this route will is for editing existing subject
# action null will take an subject id grab its values and display it on
# a table that looks like the insert_subject but id and everything else is filled out.  

@app.route('/edit_subject', methods=['GET', 'POST'])
def edit_subject():
    # check if user is login.  
    if 'username' in session:
        cur = conn.cursor()
        action = request.args.get("action" , type=int)
        id = request.args.get("id")
        if action is None:
            if id is None:
                return render_template("error.html",error="you must enter an id to edit!: ", name=escape(session['username']))
            # go an get consent, projects, diagnosis
            try: 
                pre = ('SELECT diagnosis.id, projects.id, consent.id, subject.age, subject.sex, subject.date_collection, subject.notes '
                        ' FROM subject'
                        ' INNER JOIN subject_diagnosis ON subject_diagnosis.subject_id = subject.id'
                         ' AND subject.id = %s'
                         ' INNER JOIN  diagnosis ON subject_diagnosis.diagnosis_id = diagnosis.id'
                         ' INNER JOIN subject_project ON subject_project.subject_id = subject.id'
                         ' AND subject.id = %s'
                         ' INNER JOIN  projects ON subject_project.project_id = projects.id'
                         ' INNER JOIN subject_consent ON subject_consent.subject_id = subject.id'
                         ' AND subject.id = %s'
                         ' INNER JOIN  consent ON subject_consent.consent_id = consent.id'
                         )
                cur.execute(pre, (id,id,id))
                # collect preexisting data 
                prestuff = cur.fetchall()
                age = prestuff[0][3]
                sex = {prestuff[0][4]:prestuff[0][4]}
                datec = prestuff[0][5]
                notes = prestuff[0][6]
                # there will be duplicates but we can avoid this by storing this in a dictionary
                pre_consent={}
                pre_diagnosis={}
                pre_project={}
                for r in prestuff:
                    pre_diagnosis[r[0]]=1
                    pre_project[r[1]]=1
                    pre_consent[r[2]]=1
                    
                # get all the fields necessary to draw out the inputs
                c = 'SELECT id, form FROM consent';
                cur.execute(c) 
                crows = cur.fetchall()
                # get projects
                c = 'SELECT id, name FROM projects';
                cur.execute(c) 
                prows = cur.fetchall()
                # get diagnosis
                c = 'SELECT id, disease FROM diagnosis';
                cur.execute(c)  
                drows = cur.fetchall()

            except Exception as err:
                conn.rollback() 
                return render_template("error.html",error="there was an error!: " + str(err),name=escape(session['username'])   )
            
            return render_template("edit_subject.html",name=escape(session['username']),consentSearch=crows,projectSearch=prows,diagnosisSearch=drows,age=age,sex=sex,pre_diagnosis=pre_diagnosis,pre_project=pre_project,pre_consent=pre_consent,datec=datec,notes=notes )
        else:
            ## to be done need to change insert into an update field.
            ## add this version and log 
            age =     request.args.get('age')
            sex =     request.args.get('sex')
            consent = request.values.getlist('consent_name') 
            diagnosis = request.values.getlist('diagnosis_name')
            project =   request.values.getlist('project_name')
            datec = request.args.get('datec')
            notes = request.args.get('notes')
            
            try: 
                cur.execute('BEGIN WORK;')
                insert_subject = 'INSERT INTO subject (id, users,age,sex,date_collection,timestamp,notes) VALUES (DEFAULT,%s,%s,%s,%s,DEFAULT,%s) RETURNING id;'
                cur.execute(insert_subject,(session['username'],age,sex,datec,notes))
                new_name = cur.fetchall() # gets the Serial id for the new insert
                new_serial = new_name[0][0]
                for c in consent:
                    insert_consent = 'INSERT INTO subject_consent (subject_id,consent_id,timestamp) VALUES (%s,%s,DEFAULT);'
                    cur.execute(insert_consent,(new_serial,c))
                for p in project:
                    insert_project = 'INSERT INTO subject_project (subject_id,project_id,timestamp) VALUES (%s,%s,DEFAULT);'
                    cur.execute(insert_project,(new_serial,p))
                for d in diagnosis:
                    insert_diagnosis = 'INSERT INTO subject_diagnosis (subject_id,diagnosis_id,timestamp) VALUES (%s,%s,DEFAULT);'
                    cur.execute(insert_diagnosis,(new_serial,d))
                # insert into log
                logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'subject\',%s,DEFAULT,%s);'
                lognotes = " created a new subject id: " + str(new_serial)
                cur.execute(logc,(session['username'] , lognotes))
                cur.execute('COMMIT WORK;')
                conn.commit() 
            except Exception as err:
                conn.rollback()
                return render_template("error.html",error="there was an error!: " + str(err),name=escape(session['username'])   )
            # after insertion the user has an option to insert another one action == 2 or just view all subject
            if action == 1: 
                return redirect("/view_subject")
            else:
                return redirect("/insert_subject")
            
            
    return redirect(url_for('login'))
