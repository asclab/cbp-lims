from collections import namedtuple
from cbplims import app
from flask import g
Location = namedtuple('Location', 'id parent_id parent_row parent_col project_id my_rows my_cols name notes project_name is_active')

def dim_location(id):
    cur = g.dbconn.cursor()
    Dim = namedtuple('Location', 'row col')
    if id != 0:
        sql = 'SELECT my_rows, my_cols FROM location WHERE id = %s'
        cur.execute(sql,(id,))
        record = cur.fetchone()
        cur.close()
        dim = (Dim(*record))
    else:
        dim = (Dim(0,0))
    return (dim)

def child_location(pid):
    cur = g.dbconn.cursor()
    locations = []
    if pid == 0:
        sql = ('Select l.id, l.parent_id, l.parent_row, l.parent_col, l.project_id, l.my_rows, l.my_cols, l.name, l.notes, p.name, l.is_active '
               'from location l Left JOIN projects p ON l.project_id = p.id where l.parent_id IS NULL;'
               )
        cur.execute(sql)
        for record in cur:
            locations.append(Location(*record))
    else:
        sql = ('Select l.id, l.parent_id, l.parent_row, l.parent_col, l.project_id, l.my_rows, l.my_cols, l.name, l.notes, p.name, l.is_active '
               'from location l Left JOIN projects p ON l.project_id = p.id where l.parent_id = %s;'
              )
        cur.execute(sql,(pid,))
        for record in cur:
            locations.append(Location(*record))
    cur.close()    
    
    return locations


def change_state_location(id, state):
    cur = g.dbconn.cursor()
    sql = "UPDATE location SET is_active = %s WHERE id = %s;"
    
    try:
        cur.execute(sql, (state,id))
        g.dbconn.commit()
        cur.close()
        return ("state was changed: " + id)
    except Exception as err:
        cur.close()
        return (str(err))