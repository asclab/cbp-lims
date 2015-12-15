from collections import namedtuple
from cbplims import app
from flask import g



Group = namedtuple('Group', 'id name is_admin is_view project_name is_active')

def avail_groups():
    cur = g.dbconn.cursor()
    groups = []
    sql = ('SELECT a.id, a.name, a.is_admin, a.is_view, b.name, a.is_active FROM groups a '
           'LEFT JOIN projects b ON a.project_id = b.id ORDER BY a.name'
           )
    cur.execute(sql)
    for record in cur:
        groups.append(Group(*record))
    cur.close()    
    return groups

def view_groups(gid):
    Group2 = namedtuple('Group2', 'id name is_admin is_view project_name username is_active')
    cur = g.dbconn.cursor()
    groups = []
    sql = ('SELECT a.id, a.name, a.is_admin, a.is_view, b.name, d.username, a.is_active FROM groups a '
           'LEFT JOIN projects b ON a.project_id = b.id '
           'LEFT JOIN user_groups c ON c.group_id=a.id '
           'LEFT JOIN users d ON d.id = c.user_id '
           'WHERE a.id = %s'
           'ORDER BY a.name;'
           )
    cur.execute(sql,(gid,))
    for record in cur:
        groups.append(Group2(*record))
    cur.close()    
    return groups
    


def avail_alluser():
    Group2 = namedtuple('Group2', 'id name is_admin is_view project_name username is_active')
    cur = g.dbconn.cursor()
    groups = []
    sql = ('SELECT a.id, a.name, a.is_admin, a.is_view, b.name, d.username, a.is_active FROM groups a '
           'LEFT JOIN projects b ON a.project_id = b.id '
           'LEFT JOIN user_groups c ON c.group_id=a.id '
           'LEFT JOIN users d ON d.id = c.user_id '
           'ORDER BY a.name;'
           )
    cur.execute(sql)
    for record in cur:
        groups.append(Group2(*record))
    cur.close()    
    return groups

def edit_group(gid,name,role):
    cur = g.dbconn.cursor()
    is_admin = "FALSE"
    is_view = "FALSE"
    
    if int(role) == 2:
        role = "Admins"
        is_admin = "TRUE"
    elif int(role) == 1:
        role = "Edit"
    else:
        role = "View"
        is_view = "TRUE"
    
    sql = "UPDATE groups SET name = %s, is_admin = %s, is_view = %s WHERE id = %s;"
    try: 
        cur.execute(sql, (name,is_admin,is_view,gid))
        g.dbconn.commit()
        cur.close()
        return "Group was updated "
    except Exception as err:
        g.dbconn.rollback()
        cur.close()
        return (str(err))
    
    


def add_groups(project_id,role):
    cur = g.dbconn.cursor()
    groups = []
    # get project name first.
    sql_project_name = ('SELECT name FROM projects WHERE id = %s')
    cur.execute(sql_project_name, (project_id,))
    record = cur.fetchone()
    project_name = record[0]
    
    # no need to check for contraint since error will be outputted if this did not work.
    is_admin = "FALSE"
    is_view = "FALSE"
    if int(role) == 2:
        role = "Admins"
        is_admin = "TRUE"
    elif int(role) == 1:
        role = "Edit"
    else:
        role = "View"
        is_view = "TRUE"
        
    name = project_name + ' ' + role
    sql_insert = ('INSERT INTO groups (name, project_id, is_admin, is_view) VALUES (%s, %s, %s, %s) RETURNING id')
    try: 
        cur.execute(sql_insert, (name,project_id,is_admin,is_view))
        g.dbconn.commit()
        cur.close()
        return "new group added for " + project_name
    except Exception as err:
        g.dbconn.rollback()
        cur.close()
        return (str(err))
          

def add_user_groups(user,group):
    cur = g.dbconn.cursor()
    sql = 'INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)'
    try: 
        cur.execute(sql, (user, group))
        g.dbconn.commit()
        cur.close()
        return "new user group added"
    except Exception as err:
        g.dbconn.rollback()
        cur.close()
        return (str(err))
    
def get_specific_group(project_id):
    
    Group = namedtuple('Group', 'id name is_admin is_view project_name is_active')
    cur = g.dbconn.cursor()

    groups = []
    sql = ('SELECT a.id, a.name, a.is_admin, a.is_view, b.name, a.is_active FROM groups a '
           'LEFT JOIN projects b ON a.project_id = b.id WHERE b.id = %s'
           )
    cur.execute(sql, (project_id,))
    for record in cur:
        groups.append(Group(*record))
    
    cur.close()
    if record:
        return (groups)
    
    return None

def get_user_group(user_id):
    
    Group = namedtuple('Group', 'id name is_admin is_view project_name username is_active')
    cur = g.dbconn.cursor()

    groups = []
    sql = ('SELECT a.id, a.name, a.is_admin, a.is_view, b.name, d.username, a.is_active FROM groups a '
           'LEFT JOIN projects b ON a.project_id = b.id '
           'LEFT JOIN user_groups c ON c.group_id=a.id '
           'LEFT JOIN users d ON d.id = c.user_id '
           'WHERE d.id = %s'
           'ORDER BY a.name;'
           )
    cur.execute(sql, (user_id,))
    for record in cur:
        groups.append(Group(*record))
    
    cur.close()
    if record:
        return (groups)
    
    return None



def change_state_group(gid,state):
    cur = g.dbconn.cursor()
    sql = "UPDATE groups SET is_active = %s WHERE id = %s;"
    try:
        cur.execute(sql, (state,gid))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + gid)
    except Exception as err:
        cur.close()
        return (str(err))
    

