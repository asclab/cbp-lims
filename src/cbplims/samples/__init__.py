from collections import namedtuple
from cbplims import app
from flask import g, request
import random
import string
import cbplims.location

Subjects = namedtuple('Subjects', 'id name notes is_active project_id project_name subject_types_name subject_types_id data')


def add_sample(sampletype_name,sampletype_id,subject_id,date,notes,locations,parent_location_selected,data):
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
            except Exception as err:
                cur.close()
                return str(err),''
     g.dbconn.commit()
     cur.close()
     
     #
         
     return barcode_all,name_all