from collections import namedtuple
from cbplims import app
from flask import g

Subjects = namedtuple('Subjects', 'id name notes is_active project_id project_name subject_types_name')


def list_subjects():
     cur = g.dbconn.cursor()
     subjects = []
     sql = ('Select s.id, s.name, s.notes, s.is_active,p.id, p.name, st.name FROM subjects s '
           ' LEFT JOIN projects p ON s.project_id = p.id '
           ' LEFT JOIN subject_types st ON s.subject_type_id = st.id'
          )
     cur.execute(sql)
     for record in cur:
        subjects.append(Subjects(*record))
     cur.close()    
     return subjects


def add_subjects(project_id,subject_types,name,notes):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO subjects (project_id,subject_type_id,name,notes) VALUES(%s,%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (project_id,subject_types,name,notes) )
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
     sql = ('Select s.id, s.name, s.notes, s.is_active,p.id, p.name, st.name FROM subjects s '
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
                            ' diagnosis_recorded_by diagnosis_recorded_date diagnosis_is_primary '
                            )
     cur = g.dbconn.cursor()
     diagnoses = []
     sql = ('Select s.id, s.name, s.notes, s.is_active, d.name, sd.days_from_primary, u.username, '
           ' sd.recorded_date, sd.is_primary FROM subjects s '
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
     Research_studies  = namedtuple('Research_studies', 'id name notes is_active research_study_name research_study_username research_study_date')
     cur = g.dbconn.cursor()
     research_studies = []
     sql = ('Select s.id, s.name, s.notes, s.is_active, rs.name, u.username, '
           ' ss.recorded_date FROM subjects s '
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
