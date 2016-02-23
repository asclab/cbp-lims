from collections import namedtuple
from cbplims import app
from flask import g, request, render_template
import base64

Subjects = namedtuple('Subjects', 'id name notes is_active project_id project_name subject_types_name subject_types_data data')


def list_subjects():
     cur = g.dbconn.cursor()
     subjects = []
     sql = ('Select s.id, s.name, s.notes, s.is_active,p.id, p.name, st.name, st.data, s.data FROM subjects s '
           ' LEFT JOIN projects p ON s.project_id = p.id '
           ' LEFT JOIN subject_types st ON s.subject_type_id = st.id '
           ' WHERE p.id = %s;'
          )
     cur.execute(sql ,(g.project.id,) )
     for record in cur:
        subjects.append(Subjects(*record))
     cur.close()    
     return subjects


def add_subjects(project_id,subject_types,name,notes,extra):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO subjects (project_id,subject_type_id,name,notes,data) VALUES(%s,%s,%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (project_id,subject_types,name,notes,extra) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        
        
def state(id, state):
    cur = g.dbconn.cursor()
    sql = "UPDATE subjects SET is_active = %s WHERE id = %s;"
    
    try:
        cur.execute(sql, (state,id))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + id)
    except Exception as err:
        cur.close()
        return (str(err))
    
def view_subjects(id):
     cur = g.dbconn.cursor()
     sql = ('Select s.id, s.name, s.notes, s.is_active,p.id, p.name, st.name, st.data, s.data FROM subjects s '
           ' LEFT JOIN projects p ON s.project_id = p.id '
           ' LEFT JOIN subject_types st ON s.subject_type_id = st.id '
           ' WHERE s.id = %s'
          )
     cur.execute(sql,(id,))
     record = cur.fetchone()
     subject = (Subjects(*record))
     cur.close()
     return subject
    
def view_subjects_diagnoses(id):
     Diagnoses = namedtuple('Diagnoses', 'id name notes is_active diagnosis_name diagnosis_days_from_primary '
                            ' diagnosis_recorded_by diagnosis_recorded_date diagnosis_is_primary diagnosis_id'
                            )
     cur = g.dbconn.cursor()
     diagnoses = []
     sql = ('Select s.id, s.name, s.notes, s.is_active, d.name, sd.days_from_primary, u.username, '
           ' sd.recorded_date, sd.is_primary, sd.diagnosis_id FROM subjects s '
           ' LEFT JOIN subject_diagnoses sd ON s.id = sd.subject_id '
           ' LEFT JOIN diagnoses d ON d.id = sd.diagnosis_id '
           ' LEFT JOIN users u ON sd.recorded_by=u.id'
           ' WHERE s.id = %s'
          )
     cur.execute(sql,(id,))
     for record in cur:
        diagnoses.append(Diagnoses(*record))
    
     cur.close()
     return diagnoses

def view_subjects_study(id):
     Research_studies  = namedtuple('Research_studies', 'id name notes is_active research_study_name research_study_username research_study_date research_study_study_id')
     cur = g.dbconn.cursor()
     research_studies = []
     sql = ('Select s.id, s.name, s.notes, s.is_active, rs.name, u.username, '
           ' ss.recorded_date, ss.study_id FROM subjects s '
           ' LEFT JOIN subject_study ss ON s.id = ss.subject_id '
           ' LEFT JOIN research_studies rs ON rs.id = ss.study_id '
           ' LEFT JOIN users u ON ss.recorded_by=u.id'
           ' WHERE s.id = %s'
          )
     cur.execute(sql,(id,))
     for record in cur:
        research_studies.append(Research_studies(*record))
    
     cur.close()
     return research_studies

def add_diagnosis(sid,diagnosis,days_from_primary,recorded_date,is_primary):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO subject_diagnoses (subject_id,diagnosis_id,days_from_primary,recorded_by,recorded_date,is_primary) VALUES(%s,%s,%s,%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (sid,diagnosis,days_from_primary,g.user.id,recorded_date,is_primary) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(diagnosis) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        

def delete_diagnosis(sid,did):
     cur = g.dbconn.cursor()
     sql = ('DELETE FROM subject_diagnoses WHERE subject_id = %s AND diagnosis_id = %s;') 
     
     try:
         cur.execute(sql, (sid,did) )
         g.dbconn.commit()
         cur.close()
         return ("deleted : " + str(did) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)


def add_subject_study(sid,subject_study,recorded_date):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO subject_study (subject_id,study_id,recorded_by,recorded_date) VALUES(%s,%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (sid,subject_study,g.user.id,recorded_date) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(subject_study) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        
def delete_study(sid,study):
     cur = g.dbconn.cursor()
     sql = ('DELETE FROM subject_study WHERE subject_id = %s AND study_id = %s;') 
     
     try:
         cur.execute(sql, (sid,study) )
         g.dbconn.commit()
         cur.close()
         return ("deleted : " + str(study) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        
 
def edit_subjects(project_id,subject_types,name,notes,sid,data):
     cur = g.dbconn.cursor()
     if not data:
           sql = ('UPDATE subjects SET project_id= %s, subject_type_id=%s,name=%s,notes=%s WHERE id=%s;')
           cur.execute(sql, (project_id,subject_types,name,notes,sid) )
     else:
           sql = ('UPDATE subjects SET project_id= %s, subject_type_id=%s,name=%s,notes=%s, data=%s WHERE id=%s;')
           
           cur.execute(sql, (project_id,subject_types,name,notes,data,sid) )
     try:
         
         g.dbconn.commit()
         cur.close()
         return ("edit : " + str(sid) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
     

def get_extra(f,files,subject_type):
      uploads = 'uploads/' # this is just temporary and will be moved to a global variable once its decided
      # this function used for add and edit as such the first empty string this encounters it will skip everything
      # in otherwords extra fields are always not null for every field
      extra = ''
   
      
      for key in f.keys():
           detect = str(subject_type)+"_extra_"
           
           if detect in key:
              d = request.form[key]
              if not d:
                return ""
              start = key.find(detect) + len(detect)     
              extra = extra+ "\"" + key[start:] + "\"" +":"+ "\"" + str(d) + "\","
              
              
      for key in files.keys():
           detect = str(subject_type)+"_file_"
           if detect in key:
              ufile = request.files[key]
              filename = ufile.filename 
              # encode to base64
              b64_str = base64.b64encode(ufile.read())
              start = key.find(detect) + len(detect) 
              extra = extra+ '"' + key[start:] + '":{'
              extra = extra+ '"filename":' + '"'+ str(filename) + '",'
              extra = extra+ '"mime":' + '"'+ str(ufile.mimetype) + '",'
              extra = extra+ '"base64":' + '"'+ str(b64_str) + '"},'
              
      if extra:
           extra = extra[:-1]
           extra = "{"+extra
           extra += "}"
      #return render_template("locations/temp.html", msg= str(extra) )
      return extra