from collections import namedtuple
from cbplims import app
from flask import g
Location = namedtuple('Location', 'id parent_id parent_row parent_col project_id my_rows my_cols name notes project_name is_active is_storable')

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
    # you can only add to location
    if pid == 0:
        sql = ('SELECT l.id, l.parent_id, l.parent_row, l.parent_col, p.id, l.my_rows, l.my_cols, l.name, l.notes, p.name,'
               'l.is_active,is_storable  ' 
               'FROM location l LEFT JOIN location_project lp ON l.id = lp.location_id '
               'LEFT JOIN projects p ON lp.project_id = p.id '
               'WHERE l.parent_id IS NULL AND p.id = %s;'
               )
        cur.execute(sql, (g.project.id,))
        for record in cur:
            locations.append(Location(*record))
    else:
        sql = ('SELECT l.id, l.parent_id, l.parent_row, l.parent_col, p.id, l.my_rows, l.my_cols, l.name, l.notes, p.name,'
               'l.is_active,is_storable  ' 
               'FROM location l LEFT JOIN location_project lp ON l.id = lp.location_id '
               'LEFT JOIN projects p ON lp.project_id = p.id '
               'WHERE l.parent_id = %s AND p.id = %s ; '
              )
        cur.execute(sql,(pid,g.project.id))
        for record in cur:
            locations.append(Location(*record))
    cur.close()    
    return locations


def child_location_simple(pid):
    cur = g.dbconn.cursor()
    Location = namedtuple('Location', 'id parent_row parent_col name')
    locations = []
    
    sql = ('Select id, parent_row, parent_col, name '
           'FROM location WHERE parent_id = %s; '
           )
    cur.execute(sql,(pid,))
    for record in cur:
        locations.append(Location(*record))

    cur.close()    
    return locations

def get_grand(id):
     cur = g.dbconn.cursor()
     sql = 'SELECT parent_id FROM location WHERE id = %s'
     
     cur.execute(sql,(id,))
     record = cur.fetchone()
     cur.close()
     return (record[0])

def list_location(id):
    cur = g.dbconn.cursor()
    locations = []
    sql = ('SELECT l.id, l.parent_id, l.parent_row, l.parent_col, p.id, l.my_rows, l.my_cols, l.name, l.notes, p.name,'
            'l.is_active,is_storable  ' 
            'FROM location l LEFT JOIN location_project lp ON l.id = lp.location_id '
            'LEFT JOIN projects p ON lp.project_id = p.id '
            'WHERE l.id = %s;'
          )
    cur.execute(sql,(id,))
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
    
def view_location(id):
    cur = g.dbconn.cursor()
    sql = ( 'SELECT l.id, l.parent_id, l.parent_row, l.parent_col, p.id, l.my_rows, l.my_cols, l.name, l.notes, p.name,'
            'l.is_active,is_storable  ' 
            'FROM location l LEFT JOIN location_project lp ON l.id = lp.location_id '
            'LEFT JOIN projects p ON lp.project_id = p.id '   
            ' WHERE l.id = %s;'
          )
    cur.execute(sql,(id,))
    record = cur.fetchone()
    location=(Location(*record))
    cur.close()    
    return location

def add_location(parent_id,in_row,in_col,my_row,my_col,name,notes):
    cur = g.dbconn.cursor()
     
    sql = ('INSERT INTO location (parent_id,name,parent_row,parent_col,my_rows,my_cols, notes) '
           'VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id ;'
          )
    
    if in_row == "None":
        in_row = None
        in_col = None
        
    
    try:
        cur.execute(sql,(parent_id,name,in_row,in_col,my_row,my_col,notes))
        #g.dbconn.commit()
        row = cur.fetchone()
        l_id = row[0]
        cur.close()
        return (l_id)
    
    except Exception as err:
        cur.close()
        return (str(err) + " " + sql)  


def edit_location(id,project_id,my_row,my_col,location_name,notes, is_storable):
    cur = g.dbconn.cursor()
     
    sql = ('UPDATE location SET project_id = %s,name=%s, my_rows=%s,my_cols=%s, notes=%s, '
           ' is_storable=%s WHERE id=%s ;'
          )
    
        
    
    try:
        cur.execute(sql,(project_id,location_name,my_row,my_col,notes,is_storable,id))
        g.dbconn.commit()
        cur.close()
        return ("edited location: " )
    
    except Exception as err:
        cur.close()
        return (str(err) + " " + sql)
    
def list_location_storable():
    cur = g.dbconn.cursor()
    locations = []
    sql = ('Select id, parent_id, parent_row, parent_col, my_rows, my_cols, name, notes '
           ' FROM location WHERE is_storable = \'TRUE\' AND is_active = \'TRUE\'; '
          )
    cur.execute(sql)
    Location = namedtuple('Location', 'id parent_id parent_row parent_col my_rows my_cols name notes')
    for record in cur:
        locations.append(Location(*record))
    cur.close()    
    return locations