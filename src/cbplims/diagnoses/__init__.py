from collections import namedtuple
from cbplims import app
from flask import g

Diagnoses = namedtuple('Diagnoses', 'id project_id name is_active project_name')

def list_diagnoses():
    cur = g.dbconn.cursor()
    diagnoses = []
    sql = ('Select d.id, d.project_id, d.name, d.is_active, p.name '
           'FROM diagnoses d Left JOIN projects p ON d.project_id = p.id;'
          )
    cur.execute(sql)
    for record in cur:
        diagnoses.append(Diagnoses(*record))
    cur.close()    
    return diagnoses

def view_diagnosis(did):
    cur = g.dbconn.cursor()
    diagnoses = []
    sql = ('Select d.id, d.project_id, d.name, d.is_active, p.name '
           'FROM diagnoses d Left JOIN projects p ON d.project_id = p.id WHERE d.id = %s ;'
          )
    cur.execute(sql,(did,))
    record = cur.fetchone()
    diagnoses = (Diagnoses(*record))
    cur.close()    
    return diagnoses


def edit_diagnosis(did,project_id,name):
     cur = g.dbconn.cursor()
     sql = "UPDATE diagnoses SET project_id = %s ,name=%s WHERE id= %s ;"
     
     try:
         cur.execute(sql, (project_id,name,did) )
         g.dbconn.commit()
         cur.close()
         return ("updated : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql) 


def state(id, state):
    cur = g.dbconn.cursor()
    sql = "UPDATE diagnoses SET is_active = %s WHERE id = %s;"
    
    try:
        cur.execute(sql, (state,id))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + id)
    except Exception as err:
        cur.close()
        return (str(err))
    
def add_diagnosis(project_id,name):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO diagnoses (project_id,name) VALUES(%s,%s)  ;') 
     
     try:
         cur.execute(sql, (project_id,name) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql) 
    