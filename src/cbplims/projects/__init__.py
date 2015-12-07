from collections import namedtuple
Project = namedtuple('Project', 'id name parent_id')

from cbplims import app
from flask import g


def get_available_projects(user_id):
    app.logger.debug('Finding project for user: %s', user_id)
    cur = g.dbconn.cursor()

    cur.execute('SELECT a.id, a.name, a.parent_id FROM projects a LEFT JOIN groups b ON a.id=b.project_id LEFT JOIN user_groups c ON b.id=c.group_id  WHERE c.user_id = %s;', (user_id,))

    projects = []
    for record in cur:
        print record
        projects.append(Project(record[0], record[1], record[2]))
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

    cur.execute('SELECT id, name, parent_id FROM projects WHERE id = %s;', (project_id,))

    record = cur.fetchone()
    cur.close()

    if record:
        return Project(record[0], record[1], record[2])

    return None


def new_project(name, parent_id, user_id):
    cur = g.dbconn.cursor()

    cur.execute('INSERT INTO projects (name, parent_id) VALUES (%s, %s) RETURNING id', (name, parent_id))
    row = cur.fetchone()
    project_id = row[0]

    app.logger.debug("New project: %s (%s)", project_id, name)

    cur.execute('INSERT INTO groups (name, project_id, is_admin) VALUES (%s, %s, TRUE) RETURNING id', ('%s Admins' % name, project_id))
    row = cur.fetchone()
    group_id = row[0]

    app.logger.debug("New group: %s (%s)", group_id, '%s Admins' % name)

    cur.execute('INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)', (user_id, group_id))

    cur.close()
    g.dbconn.commit()

    return project_id

def avail_projects():
    cur = g.dbconn.cursor()
    projects = []
    sql = "SELECT id, name, parent_id FROM projects"
    try:
        cur.execute(sql)
        record = cur.fetchone()
        for record in cur:
            projects.append(Project(record[0], record[1], record[2]))
    except:
        return projects
    cur.close()
    return projects

def add_projects(name,parent):
    cur = g.dbconn.cursor()
    try:
        if int(parent) == -1:
            cur.execute("INSERT INTO projects (name) VALUES (%s) RETURNING id",(name,))
        else:
            cur.execute("INSERT INTO projects (name,parent_id) VALUES (%s,%s) RETURNING id",(name,parent))
        g.dbconn.commit()
        row = cur.fetchone()
        cur.close()
        out = "Inserted " + str(row[0])
        return (out)
    except Exception as err:
        g.dbconn.rollback()
        cur.close()
        return (str(err))
