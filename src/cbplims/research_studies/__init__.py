from collections import namedtuple
from cbplims import app
from flask import g

Research_studies = namedtuple('Research_studies', 'id project_id name description date_active is_active project_name')


def list_research_studies():
     cur = g.dbconn.cursor()
     research_studies = []
     sql = ('Select d.id, d.project_id, d.name, d.description, d.date_active, d.is_active, p.name '
           'FROM research_studies d Left JOIN projects p ON d.project_id = p.id;'
          )
     cur.execute(sql)
     for record in cur:
        research_studies.append(Research_studies(*record))
     cur.close()    
     return research_studies
    
def view_research_studies(rid):
     cur = g.dbconn.cursor()
     research_studies = []
     sql = ('Select d.id, d.project_id, d.name, d.description, d.date_active, d.is_active, p.name '
           'FROM research_studies d Left JOIN projects p ON d.project_id = p.id WHERE d.id = %s ;'
          )
     cur.execute(sql,(rid,))
     record = cur.fetchone()
     research_studies = (Research_studies(*record))
     cur.close()    
     return research_studies
    
def edit_research_studies(rid,project_id,name,description,date):
     cur = g.dbconn.cursor()
     sql = "UPDATE research_studies SET project_id = %s ,name=%s, description=%s, date_active=%s WHERE id= %s ;"
     
     try:
         cur.execute(sql, (project_id,name,description, date, rid) )
         g.dbconn.commit()
         cur.close()
         return ("updated : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        
def state(id, state):
    cur = g.dbconn.cursor()
    sql = "UPDATE research_studies SET is_active = %s WHERE id = %s;"
    
    try:
        cur.execute(sql, (state,id))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + id)
    except Exception as err:
        cur.close()
        return (str(err))
    
    
def add_research_studies(project_id,name,description,date):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO research_studies (project_id,name,description,date_active) VALUES(%s,%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (project_id,name,description,date) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)