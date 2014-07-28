'''
mediaserver.py:

CherryPy media server class handles POST data from network media clients
that send surveillance images to the media server for processing, archiving
in a database, and storage to disk.
'''

import cherrypy
import threading

from datetime import datetime, timedelta
from database import Database
from Queue import Queue
from utils import Utils

class MediaServer(object):    
    '''
    Media server for internal camera clients to upload images.
    '''
      
    def __init__( self, db_name ):
        self.db_name = db_name
        
        # Subscribe to the CherryPy start/stop events for init/cleanup
        cherrypy.engine.subscribe('start', self.setup)
        cherrypy.engine.subscribe('stop', self.cleanup)

    #==========================================================================
    # CherryPy Engine Setup / Cleanup
    #==========================================================================
    def setup( self ):
        '''
        Called on CherryPy engine start.
        '''
        
        # Connect to the DB
        self.db = Database()
        self.db.connect( self.db_name )
        
        # Start the image worker thread
        self.run = True
        self.queue = Queue()
        self.t_media = threading.Thread( name='img_worker', target=self.img_worker)
        self.t_media.start()
    
    def cleanup( self ):
        '''
        Called on CherryPy engine stop.
        '''
        
        self.run = False

    #==========================================================================
    # Image Processing Thread
    #==========================================================================    
    def img_worker( self ):
        '''
        Method run by the img_worker. Polls the image queue, pulling images
        off, processing them, and inserting them into the DB one by one.
        '''
        
        while( self.run ):
            size = self.queue.qsize()
            if size > 0:
                content_type, camid, timestamp, rotate, raw = self.queue.get()
                full_path, thumb_path = Utils.process_image( camid, timestamp, raw, rotate )
                self.db.insert_image( camid, content_type, full_path, thumb_path, timestamp )
    
    #==========================================================================
    # CherryPy HTTP/URL Handlers
    #==========================================================================
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ready( self ):
        '''
        /ready
        
        Returns a simple json dict indicating whether the server is ready to 
        accept or serve images.
        '''
        return { 'ready' : self.db.is_ready(), }
    
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
        
        camid = self.db.get_camid_for_desc( data['desc'] )
            
        if camid == None:
            camid = self.db.insert_camera( data['desc'] )
            
        return { 'camid' : camid }
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def multiupload( self, camid=0, rotate=0, length=[] ):
        '''
        /multiupload?camid=X&rotate=Y&length=Z1&length=Z2&...&length=Zn
        
        Inserts metadata about the uploaded image into the DB and saves the 
        image to disk.
        
        Returns a JSON struct containing the camids and timestamps necessary to
        access the images once they've been post-processed and made available
        through the web server. 
        '''
        
        content_length = cherrypy.request.headers['Content-Length']
        content_type = cherrypy.request.headers['Content-Type']
        raw = cherrypy.request.body.read( int( content_length ) )
        
        if self.db.get_desc_for_camid( camid ) == None:
            return { 'camids' : [], 'timestamps' : [] }
            
        if type( length ) != type( [] ):
            length = [length, ]
        
        if content_type == 'image/jpeg':
            now = datetime.now()
            delta = timedelta( microseconds=1 )
        
            camids = []
            timestamps = []
                
            for img_len in length:
                img_len = int( img_len )
                img = raw[:img_len]
                raw = raw[img_len:]
                
                timestamp = Utils.timestamp_datetime_to_str( now )
                self.queue.put( (content_type, camid, timestamp, rotate, img) )

                camids.append( camid )
                timestamps.append( timestamp )
                now += delta
            
            return { 'camids' : camids, 'timestamps' : timestamps }
        
        return { 'camids' : [], 'timestamps' : [] }
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload( self, camid=0, rotate=0 ):
        '''
        /upload?camid=X&rotate=Y
        
        Puts metadata for the uploaded image image along with the image data
        into a queue for processing by the img_worker. 
        
        Returns a JSON struct containing the camid and timestamp necessary to
        access the image once it's been post-processed and made available
        through the web server. 
        '''
        length = cherrypy.request.headers['Content-Length']
        content_type = cherrypy.request.headers['Content-Type']
        raw = cherrypy.request.body.read( int( length ) )
        
        if self.db.get_desc_for_camid( camid ) == None:
            return { 'camid' : -1, 'timestamp' : "-1" }
        
        if content_type == 'image/jpeg':  
            timestamp = Utils.timestamp_now_str()
            self.queue.put( (content_type, camid, timestamp, rotate, raw) )
            
            return { 'camid' : camid, 'timestamp' : timestamp }
        
        return { 'camid' : -1, 'timestamp' : "-1" }