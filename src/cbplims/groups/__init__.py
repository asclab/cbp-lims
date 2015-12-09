from collections import namedtuple
from cbplims import app
from flask import g



Project = namedtuple('Group', 'id project_id name is_admin is_view project_name')

def avail_groups():
    cur = g.dbconn.cursor()
    groups = []
    sql = "SELECT id, project_id, name, is_admin, is_view FROM groups;"
    cur.execute(sql)

    for record in cur:
        sql2 = "SELECT name FROM projects WHERE id = %s;"
        cur2 = g.dbconn.cursor()
        cur2.execute(sql2,(record[1],))
        temp = cur2.fetchone()
        project_name = temp[0]
        cur2.close()
        record = record + (project_name,)
        groups.append(Project(*record))
    cur.close()    
    return groups