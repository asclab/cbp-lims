from collections import namedtuple
Project = namedtuple('Project', 'id name parent_id')

from cbplims import conf, app


def get_available_projects(user_id):
    with conf.conn() as conn:
        app.logger.debug('Finding project for user: %s', user_id)
        cur = conn.cursor()

        cur.execute('SELECT a.id, a.name, a.parent_id FROM projects a LEFT JOIN groups b ON a.id=b.project_id LEFT JOIN user_groups c ON b.id=c.group_id  WHERE c.user_id = %s;', (user_id,))

        projects = []
        for record in cur:
            print record
            projects.append(Project(record[0], record[1], record[2]))
        cur.close()

        return projects


def get_project(project_id):
    with conf.conn() as conn:
        cur = conn.cursor()

        cur.execute('SELECT id, name, parent_id FROM projects WHERE id = %s;', (project_id,))

        record = cur.fetchone()
        cur.close()

        if record:
            return Project(record[0], record[1], record[2])

        return None


def new_project(name, parent_id, user_id):
    with conf.conn() as conn:
        cur = conn.cursor()

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
        conn.commit()

        return project_id
