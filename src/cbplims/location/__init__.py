from collections import namedtuple
from cbplims import app
from flask import g
Location = namedtuple('Location', 'id parent_id parent_row parent_col project_id my_rows my_cols name notes project_name')


def child_location(pid):
    cur = g.dbconn.cursor()
    locations = []
    if pid == 0:
        sql = ('Select l.id, l.parent_id, l.parent_row, l.parent_col, l.project_id, l.my_rows, l.my_cols, l.name, l.notes, p.name '
               'from location l Left JOIN projects p ON l.project_id = p.id where l.parent_id IS NULL;'
               )
        cur.execute(sql)
        for record in cur:
            locations.append(Location(*record))
    else:
        sql = ('Select l.id, l.parent_id, l.parent_row, l.parent_col, l.project_id, l.my_rows, l.my_cols, l.name, l.notes, p.name '
               'from location l Left JOIN projects p ON l.project_id = p.id where l.parent_id = %s;'
              )
        cur.execute(sql,(pid,))
        for record in cur:
            locations.append(Location(*record))
    cur.close()    
    
    return locations