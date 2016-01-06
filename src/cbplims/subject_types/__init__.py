from collections import namedtuple
from cbplims import app
from flask import g

Subject_types = namedtuple('Subject_types', 'id project_id name is_active fields project_name')

def list_subject_types():
     cur = g.dbconn.cursor()
     subject_types = []
     sql = ('Select d.id, d.project_id, d.name, d.is_active, d.fields, p.name '
           'FROM subject_types d Left JOIN projects p ON d.project_id = p.id;'
          )
     cur.execute(sql)
     for record in cur:
        subject_types.append(Subject_types(*record))
     cur.close()    
     return subject_types
    
def view_subject_types(sid):
     cur = g.dbconn.cursor()
     research_studies = []
     sql = ('Select d.id, d.project_id, d.name, d.is_active, d.fields, p.name '
           'FROM subject_types d Left JOIN projects p ON d.project_id = p.id WHERE d.id = %s ;'
          )
     cur.execute(sql,(sid,))
     record = cur.fetchone()
     research_studies = (Subject_types(*record))
     cur.close()    
     return research_studies
    
def edit_subject_types(sid,project_id,name,fields):
     cur = g.dbconn.cursor()
     sql = "UPDATE subject_types SET project_id = %s ,name=%s, fields=%s WHERE id= %s ;"
     
     try:
         cur.execute(sql, (project_id,name,fields, sid) )
         g.dbconn.commit()
         cur.close()
         return ("updated : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        
def state(id, state):
    cur = g.dbconn.cursor()
    sql = "UPDATE subject_types SET is_active = %s WHERE id = %s;"
    
    try:
        cur.execute(sql, (state,id))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + id)
    except Exception as err:
        cur.close()
        return (str(err))
    
def add_subject_types(project_id,name,fields):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO subject_types (project_id,name,fields) VALUES(%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (project_id,name,fields) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)