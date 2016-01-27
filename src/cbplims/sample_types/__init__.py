from collections import namedtuple
from cbplims import app
from flask import g, request

Sample_types = namedtuple('Sample_types', 'id project_id name description is_active project_name data')


def list_sample_types():
     cur = g.dbconn.cursor()
     sample_types = []
     sql = ('Select d.id, d.project_id, d.name, d.description, d.is_active, p.name, d.data '
           'FROM sample_types d Left JOIN projects p ON d.project_id = p.id '
           'WHERE p.id = %s; '
          )
     cur.execute(sql,(g.project.id,) )
     for record in cur:
        sample_types.append(Sample_types(*record))
     cur.close()    
     return sample_types
    
def view_sample_types(rid):
     cur = g.dbconn.cursor()
     sample_types = []
     sql = ('Select d.id, d.project_id, d.name, d.description, d.is_active, p.name, d.data '
           'FROM sample_types d Left JOIN projects p ON d.project_id = p.id WHERE d.id = %s ;'
          )
     cur.execute(sql,(rid,))
     record = cur.fetchone()
     sample_types = (Sample_types(*record))
     cur.close()    
     return sample_types
    
def edit_sample_types(rid,project_id,name,description,extra):
     cur = g.dbconn.cursor()
     sql = "UPDATE sample_types SET project_id = %s ,name=%s, description=%s, data=%s WHERE id= %s ;"
     
     try:
         cur.execute(sql, (project_id,name,description, extra, rid) )
         g.dbconn.commit()
         cur.close()
         return ("updated : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
        
def state(id, state):
    cur = g.dbconn.cursor()
    sql = "UPDATE sample_types SET is_active = %s WHERE id = %s;"
    
    try:
        cur.execute(sql, (state,id))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + id)
    except Exception as err:
        cur.close()
        return (str(err))
    
    
def add_sample_types(project_id,name,description):
     cur = g.dbconn.cursor()
     sql = ('INSERT INTO sample_types (project_id,name,description) VALUES(%s,%s,%s)  ;') 
     
     try:
         cur.execute(sql, (project_id,name,description) )
         g.dbconn.commit()
         cur.close()
         return ("add : " + str(name) )
    
     except Exception as err:
         cur.close()
         return (str(err) + " " + sql)
     
def get_extra(f):
      extra = "{"
      
      
      for key in f.keys():
           for value in f.getlist(key):
              if "data_" in key:
                  d = request.form[key]
                  start = key.find("data_") + len("data_")   
                  d2 = request.form["type_"+str(key[start:])]
                  extra = extra+ "\"" + d + "\"" +":"+ "\"" + d2 + "\","
                  
      if extra:
           extra = extra[:-1]
           extra += "}"
      return extra
