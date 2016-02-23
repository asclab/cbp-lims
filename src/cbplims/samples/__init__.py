from collections import namedtuple
from cbplims import app
from flask import g, request
import random
import string
import cbplims.location

Sample = namedtuple('Samples', 'id name barcode time_entered date_collection location_id notes extra')

def get_children(subject):
     cur=g.dbconn.cursor()
     children = []
     sql = ('SELECT sa.name, sa.id  FROM sample sa '
            ' LEFT JOIN subjects sb ON sb.id = sa.subject_id '
            ' WHERE sb.id = %s'
            )
     cur.execute(sql,(subject,))
     for record in cur:
          children.append(record)
     cur.close()
     
     return children

def list_small_sample():
     cur=g.dbconn.cursor()
     samples = []
     # need to add project_id to table sample
     sql = 'SELECT s.id, s.name, subjects.name FROM sample s LEFT JOIN subjects ON subjects.id  = s.subject_id'
     cur.execute(sql)
     for record in cur:
          samples.append(record)
     return samples

def view_samples_by_subject(subject):
     cur = g.dbconn.cursor()
     sample = []
     sql =  ('SELECT s.id, s.name, s.barcode, s.time_entered, s.date_collection, s.location_id, s.notes, s.data '
             ' FROM sample s LEFT JOIN sample_types st ON st.id = s.sampletype_id '
             ' WHERE s.subject_id = %s '
           )
     cur.execute(sql,(subject,))
     for record in cur:
               
           sample.append(   Sample(*record)   )
     cur.close()
     return sample
def add_sample(sampletype_name,sampletype_id,subject_id,date,notes,locations,parent_location_selected,data,parent_samples):
     cur = g.dbconn.cursor()
     # insert into location first
     # follow by sample
      # multiple locations are allow
      # multiple locations are allow
      # for each location a new entry will be submitted
      # a new name for the sample will be created automatically
      # subject#_sample#_tissue_type
     barcode_all = []
     name_all = []
      
     for l in locations:
            location = l.split("_")
            barcode = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
            
            # check if parent_row and parent_col exists
            sql_c = ('SELECT id FROM location WHERE parent_id = %s AND ')
            
            sql_loc = ('INSERT INTO location (parent_id,name,project_id,parent_row,parent_col,my_rows,my_cols,notes,is_storable,barcode) '
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id ;'
                  )
            # insert into location first
            # return a location id.
            # name is empty because we need sample id
            try: 
               cur.execute(sql_loc,(parent_location_selected,'name',g.project.id,location[0],location[1],0,0,notes,False,barcode))
               row = cur.fetchone()
               lid = row[0]               
               sql = ('INSERT INTO sample (barcode,subject_id,sampletype_id,date_collection,users,location_id,notes,data) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id  ;')
               cur.execute(sql,(barcode,subject_id,sampletype_id,date,g.user.id,lid,notes,data))
               row = cur.fetchone()
               sid = row[0]
               name = str(subject_id)+"_"+str(sid)+"_"+ sampletype_name
               # update name for both sample and location here
               sql_update_l = 'UPDATE location SET name=%s WHERE id=%s'
               cur.execute(sql_update_l,(name,lid))
               sql_update_s = 'UPDATE sample SET name=%s WHERE id=%s'
               cur.execute(sql_update_s,(name,sid))
               barcode_all.append(barcode)
               name_all.append(name)
               # still need to add sample_child relation here
               sql_cp = ('INSERT INTO sample_parent_child (child,parent) VALUES(%s,%s)')
               if not parent_samples:
                    cur.execute(sql_cp,(sid,sid))
               else:
                    for p in parent_samples:
                         cur.execute(sql_cp,(sid,p))
            except Exception as err:
                cur.close()
                return str(err),''
     g.dbconn.commit()
     cur.close()
     
     #
         
     return barcode_all,name_all