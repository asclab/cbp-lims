from collections import namedtuple
from cbplims import app
from flask import g



Project = namedtuple('Group', 'id name is_admin is_view project_name')

def avail_groups():
    cur = g.dbconn.cursor()
    groups = []
    sql = "SELECT a.id, a.name, a.is_admin, a.is_view, b.name FROM groups a LEFT JOIN projects b ON a.project_id = b.id"
    cur.execute(sql)

    for record in cur:
        groups.append(Project(*record))
    cur.close()    
    return groups