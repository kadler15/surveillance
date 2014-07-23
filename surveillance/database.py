'''
mediaclient.py:

Media client for the network cameras to send
image data to the media server.
'''

import os
import sqlite3

class Database(object):
    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = Database()
        return cls.Instance
    
    def __init__(self):
        self.conn = None
        self.c = None
        self.ready = False
        
    def connect(self, db_filename):
        db_is_new = not os.path.exists(db_filename)
        self.conn = sqlite3.connect(db_filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        
        if db_is_new:
            self.init_schema()
            
        self.ready = True
                
    def init_schema(self):
        self.c.execute( 'CREATE TABLE Images' 
                        ' (Id INTEGER PRIMARY KEY, LocId INTEGER,' 
                        ' ImageExt TEXT, ThumbPath TEXT, FullPath TEXT, Ts DATETIME,' 
                        ' FOREIGN KEY(LocId) REFERENCES Locations(Id))' )
        
        self.c.execute( 'CREATE TABLE Cameras(Id INTEGER PRIMARY KEY, Desc TEXT NOT NULL UNIQUE)' )
        
    def is_ready(self):
        return self.ready
    
    def insert_image(self, loc_id, ext, thumbpath, fullpath, timestamp):
        self.c.execute( 'INSERT INTO Images VALUES(?, ?, ?, ?, ?, ?)', 
                        (None, loc_id, ext, thumbpath, fullpath, timestamp) )
        
        return self.c.lastrowid
        
    def insert_camera(self, desc):
        self.c.execute( 'INSERT INTO Cameras(Desc) VALUES(NULL, ?)', (desc,) )
        
        # Return the UID
        return self.c.lastrowid
        
    def get_camera_id_for_desc(self, desc):
        self.c.execute( 'SELECT Id FROM Cameras WHERE Desc=?', (desc,) )
        
        row = self.c.fetchone()
        return row['Id'] if row != None else None
    
    def get_desc_for_camera_id(self, loc_id):
        self.c.execute( 'SELECT Desc FROM Cameras WHERE Id=?', (loc_id,) )
        
        row = self.c.fetchone()
        return row['Desc'] if row != None else None
    
    def get_most_recent_thumbs(self, limit):
        self.c.execute( 'SELECT Ts, LocId, ImageExt, ThumbPath FROM Images' 
                        ' ORDER BY datetime(Ts) DESC' )
        
        rows = self.c.fetchmany(limit)
        return rows
    
    def get_thumbs_for_range(self, start, end):
        self.c.execute( 'SELECT Ts, LocId ImageExt, ThumbPath FROM Images'
                        ' WHERE Ts BETWEEN datetime(?) AND datetime(?)'
                        ' ORDER BY datetime(Ts) DESC', (start, end) )
        
    def get_full_image_for_id(self, img_id):
        self.c.execute( 'SELECT FullPath FROM Images'
                        ' WHERE Id=?', (img_id,) )
        
        row = self.c.fetchone()
        return row['Full'] if row != None else None