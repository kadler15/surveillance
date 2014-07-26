'''
databasecpy.py:

Database helpers.
'''

from utils import Utils

from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Sequence, Text, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Image(Base):
    '''
    Bound to images table in DB.
    '''
    
    __tablename__ = 'images'
    imgid = Column( Integer, Sequence( 'imgid_seq' ), primary_key=True )
    camid = Column( Integer, ForeignKey( 'cameras.camid' ), nullable=False )
    content_type = Column( Text, nullable=False )
    thumb = Column( Text, nullable=False, unique=True )
    full = Column( Text, nullable=False, unique=True )
    timestamp = Column( DateTime, nullable=False )
    __table_args__ = (UniqueConstraint( 'camid', 'timestamp', name='_camid_timestamp_uc' ), )
    
    def __repr__(self):
        return "<Image(imgid='{0}', camid='{1}', content_type='{2}', thumb='{3}', full='{4}', timestamp='{5}')>".\
            format( self.imgid, self.camid, self.content_type, self.thumb, self.full, self.timestamp )
        
class Camera(Base):
    '''
    Bound to cameras table in DB.
    '''

    __tablename__ = 'cameras'
    camid = Column( Integer, Sequence( 'camid_seq' ), primary_key=True )
    desc = Column( Text, nullable=False, unique=True )
    
    def __repr__(self):
        return "<Camera(camid='{0}', desc='{1}')>".format( self.camid, self.desc )

class Database(object):
    '''
    Database wrapper to provide easier access to SQL Alchemy
    SQLite database.
    '''
    
    def __init__( self ):
        self.db = None
        self.ready = False
        
    def connect( self, db_filename ):
        '''
        Connect to the DB and configure binding.
        '''
        
        self.db = create_engine( 'sqlite:///{0}'.format( db_filename ) )
        self.Session = sessionmaker()
        self.Session.configure( bind=self.db )
        Base.metadata.create_all( bind=self.db )
            
        self.ready = True
        
    def is_ready( self ):
        '''
        Returns True if the DB engine is created and configured.
        '''
        
        return self.ready
    
    def insert_image( self, camid, content_type, thumbpath, fullpath, timestamp ):
        '''
        Insert a fully-specified image into the images table.
        
        Returns the imgid.
        '''
        
        session = self.Session()
        
        timestamp = Utils.timestamp_str_to_datetime( timestamp )
        
        image = Image( camid=camid, content_type=content_type, 
                       thumb=thumbpath, full=fullpath, timestamp=timestamp )
        
        session.add( image )
        session.commit()
        
        return image.imgid
        
    def insert_camera( self, desc ):
        '''
        Insert a camera with the provided description into the
        cameras table.

        Returns the camid.
        '''
        
        session = self.Session()
        
        camera = Camera( desc=desc )
        
        session.add( camera )
        session.commit()
        
        return camera.camid
        
    def get_camid_for_desc( self, desc ):
        '''
        Return the camid for the camera with the provided description.
        Return None if not found.
        '''
        
        session = self.Session()
        
        for row in session.query(Camera).\
                    filter(Camera.desc==desc):
            return row.camid
        
        return None
    
    def get_desc_for_camid( self, camid ):
        '''
        Return the description for the provided camid.
        Return None if not found.
        '''
        
        session = self.Session()
        
        for row in session.query( Camera ).\
                    filter( Camera.camid==camid ):
            return row.desc
        
        return None
    
    def get_most_recent_images( self, limit ):
        '''
        Get a list of the most recent images, up to the specified
        limit.
        
        Returns a list of tuples (camid, timestamp).
        '''
        
        session = self.Session()
        
        imgs = []
        for row in session.query( Image ).\
                    order_by( Image.timestamp )[:limit]:
            imgs.append( (row.camid, Utils.timestamp_datetime_to_str( row.timestamp ) ) )

        return imgs
    
    def get_most_recent_images_for_camid( self, camid, limit ):
        '''
        Get a list of the most recent images, up to the specified
        limit, for a camid.
        
        Returns a list of tuples (camid, timestamp).
        '''
        
        session = self.Session()
        
        imgs = []
        for row in session.query( Image ).\
                    filter( Image.camid==camid ).\
                    order_by( Image.timestamp )[:limit]:
            imgs.append( (row.camid, Utils.timestamp_datetime_to_str( row.timestamp ) ) )

        return imgs
    
    def get_images_for_range( self, start, end ):
        '''
        Get a list of the images between timestamps start and end.
        
        Returns a list of tuples (camid, timestamp).
        '''
        
        session = self.Session()
        
        start = Utils.timestamp_str_to_datetime( start )
        end = Utils.timestamp_str_to_datetime( end )
        
        imgs = []
        for row in session.query( Image ).\
                    filter( Image.timestamp > start ).\
                    filter( Image.timestamp < end ).\
                    order_by( Image.timestamp ):
            imgs.append( (row.camid, Utils.timestamp_datetime_to_str( row.timestamp ) ) )
                    
        return imgs
    
    def get_images_for_range_camid( self, camid, start, end ):
        '''
        Get a list of the images between timestamps start and end
        for the provided camid. List of tuples (camid, timestamp).
        '''
        
        session = self.Session()
        
        start = Utils.timestamp_str_to_datetime( start )
        end = Utils.timestamp_str_to_datetime( end )
        
        imgs = []
        for row in session.query( Image ).\
                    filter( Image.camid==camid).\
                    filter( Image.timestamp > start ).\
                    filter( Image.timestamp < end ).\
                    order_by( Image.timestamp ):
            imgs.append( (row.camid, Utils.timestamp_datetime_to_str( row.timestamp ) ) )
                    
        return imgs
    
    def get_thumb_path_for_image( self, camid, timestamp ):
        '''
        Get the thumb-image path for the provided camid and
        timestamp. 
        
        Returns a tuple (content type, path) or None.
        '''
        
        session = self.Session()
        
        timestamp = Utils.timestamp_str_to_datetime( timestamp )
        
        for row in session.query( Image ).\
                    filter( Image.camid==camid ).\
                    filter( Image.timestamp==timestamp):
            return (row.content_type, row.thumb)
        
        return None
        
    def get_full_path_for_image( self, camid, timestamp ):
        '''
        Get the full-image path for the provided camid and
        timestamp. 
        
        Returns a tuple (content type, path) or None.
        '''
        
        session = self.Session()
        
        timestamp = Utils.timestamp_str_to_datetime( timestamp )
        
        for row in session.query( Image ).\
                    filter( Image.camid==camid ).\
                    filter( Image.timestamp==timestamp ):
            return (row.content_type, row.full)
        
        return None