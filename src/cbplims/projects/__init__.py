from collections import namedtuple
Project = namedtuple('Project', 'id name parent_id code is_active')

from cbplims import app
from flask import g


def get_available_projects(user_id):
    app.logger.debug('Finding project for user: %s', user_id)
    cur = g.dbconn.cursor()
                         
    cur.execute('SELECT a.id, a.name, a.parent_id, a.code, a.is_active FROM projects a LEFT JOIN groups b ON a.id=b.project_id LEFT JOIN user_groups c ON b.id=c.group_id  WHERE c.user_id = %s;', (user_id,))

    projects = []
    for record in cur:
        print record
        projects.append(Project(record[0], record[1], record[2], record[3], record[4]))
    cur.close()

    return projects


def get_project_auth_level(user_id, project_id):
    app.logger.debug('Finding project permissions for project: %s, for user: %s', project_id, user_id)
    cur = g.dbconn.cursor()

    cur.execute('SELECT a.is_admin, a.is_view FROM groups a LEFT JOIN user_groups b ON a.id=b.group_id  WHERE b.user_id = %s AND a.project_id = %s;', (user_id, project_id,))

    is_view = True
    for record in cur:
        if record[0]:
            return 'admin'
        if not record[1]:
            is_view = False
    cur.close()

    return 'view' if is_view else 'rw'


def get_project(project_id):
    cur = g.dbconn.cursor()

    cur.execute('SELECT id, name, parent_id, code, is_active FROM projects WHERE id = %s;', (project_id,))

    record = cur.fetchone()
    cur.close()

    if record:
        return Project(record[0], record[1], record[2], record[3], record[4])

    return None


def new_project(name, code, parent_id=-1):
    cur = g.dbconn.cursor()
    # no parents
    try:
        if int(parent_id) == -1:
            cur.execute('INSERT INTO projects (name,code) VALUES (%s,%s) RETURNING id', (name,code ))
        else:
            cur.execute('INSERT INTO projects (name, parent_id, code) VALUES (%s, %s, %s) RETURNING id', (name, parent_id, code))
        row = cur.fetchone()
        project_id = row[0]
        app.logger.debug("New project: %s (%s)", project_id, name)
        cur.execute('INSERT INTO groups (name, project_id, is_admin) VALUES (%s, %s, TRUE) RETURNING id', ('%s Admins' % name, project_id))
        row = cur.fetchone()
        group_id = row[0]
        app.logger.debug("New group: %s (%s)", group_id, '%s Admins' % name)
        cur.execute('INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)', (g.user.id, group_id))
        cur.close()
        g.dbconn.commit()
    except Exception as err:
        g.dbconn.rollback()
        cur.close()
        return (str(err))
    
    return  ("Inserted " + str(project_id))

def avail_projects():
    cur = g.dbconn.cursor()
    projects = []
    sql = "SELECT id, name, parent_id, code, is_active FROM projects;"
    try:
        cur.execute(sql)
        
        for record in cur:
            projects.append(Project(record[0], record[1], record[2], record[3], record[4]))
            
    except Exception as err:
        cur.close()
        return (str(err))
    cur.close()
    return projects



def get_projects_recursive(parent_id=None, indent=0, project_list=None):
    indent += 1
    if not project_list:
        project_list = []

    cur = g.dbconn.cursor()

    if parent_id:
        sql = "SELECT id, name, parent_id, code, is_active FROM projects WHERE parent_id = %s ORDER BY name;"
        args = [parent_id,]
    else:
        sql = "SELECT id, name, parent_id, code, is_active FROM projects WHERE parent_id is NULL ORDER BY name;"
        args = []

    cur.execute(sql, args)

    for record in cur:
        project_list.append((indent, Project(*record)))
        get_projects_recursive(record[0], indent, project_list)

    cur.close()
    return project_list

def promote_projects_child(parent_id,child_id):
    # get grandparent
    cur = g.dbconn.cursor()
    sql = "SELECT parent_id FROM projects WHERE id = %s;"
    cur.execute(sql, (parent_id, ))
    row = cur.fetchone()
    grand_parent_id = row[0]
    
    sql2 = "UPDATE projects SET parent_id = %s WHERE id = %s;"
    cur.execute(sql2, (grand_parent_id, child_id))
    g.dbconn.commit()
    cur.close()
    return

def change_state_project(id,state):
    cur = g.dbconn.cursor()
    sql = "UPDATE projects SET is_active = %s WHERE id = %s;"
    cur.execute(sql, (state, id))
    g.dbconn.commit()
    cur.close()
    return 1

    