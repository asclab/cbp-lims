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