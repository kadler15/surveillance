import cherrypy

from database import Database
from utils import Utils

class MediaServer(object):    
    '''
    Media server for internal camera clients to upload images.
    '''
      
    def __init__( self, db_name ):
        self.db_name = db_name
        self.database = None
        
    def db( self ):
        if self.database == None:
            self.database = Database()
            self.database.connect( self.db_name )
            
        return self.database
    
    @cherrypy.expose
    def index( self ):
        return cherrypy.NotFound
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ready( self ):
        '''
        /ready
        
        Returns a simple json dict indicating whether
        the server is ready to accept or serve images.
        '''
        return { 'ready' : self.db().is_ready(), }
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def register( self ):
        '''
        /register
        
        Registers the camera with the description provided via JSON. 
        
        Returns a JSON response with the camid.
        '''
        
        data = cherrypy.request.json
        
        camid = self.db().get_camid_for_desc( data['desc'] )
            
        if camid == None:
            camid = self.db().insert_camera( data['desc'] )
            
        return { 'camid' : camid }
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload( self, camid=0 ):
        '''
        /upload?camid=X
        
        Inserts metadata about the uploaded image into the DB
        and saves the image to disk.
        
        Returns a JSON struct containing the imgid and an error
        flag indicating whether or not the upload was successful
        and whether or not the imgid is valid.
        '''
        
        length = cherrypy.request.headers['Content-Length']
        content_type = cherrypy.request.headers['Content-Type']
        raw = cherrypy.request.body.read( int( length ) )
        
        if self.db().get_desc_for_camid( camid ) == None:
            return { 'imgid' : -1, 'error' : 1 }
        
        if content_type == 'image/jpeg':           
            timestamp = Utils.timestamp_now_str()
            path = 'images/{0}_{1}.jpg'.format( camid, timestamp )
            f = open( path, 'wb' )
            f.write( raw )
            f.close()
            
            imgid = self.db().insert_image( camid, content_type, path, path, timestamp )
            
            return { 'imgid' : imgid, 'error' : 0 }
        
        return { 'imgid' : -1, 'error' : 1 }