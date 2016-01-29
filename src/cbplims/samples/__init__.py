from collections import namedtuple
from cbplims import app
from flask import g, request

Subjects = namedtuple('Subjects', 'id name notes is_active project_id project_name subject_types_name subject_types_id data')


def add_sample(sample_type,subject,date,lid,notes):
     cur = g.dbconn.cursor()
     # insert into location first
     # follow by sample
     sql = ('INSERT INTO sample (sampletype_id,date_collection,users,location_id,notes) VALUES(%s,%s,%s,%s,%s)  ;') 
     subjects = []
     cur.execute(sql,(sample_type,date,g.user.id,lid,notes))
     g.dbconn.commit()
     cur.close()    
     return subjects