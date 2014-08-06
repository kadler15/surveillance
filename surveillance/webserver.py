'''
webserver.py:

CherryPy web server class exposes URLs that allow access to archived 
surveillance images.
'''

import cherrypy

from database import Database
from datetime import datetime
from utils import Utils

class WebServer(object):
    '''
    Web server for external web clients to access archived imagery.
    '''
    
    def __init__( self, db_name ):
        self.db_name = db_name
        
        cherrypy.engine.subscribe('start', self.setup)
        cherrypy.engine.subscribe('stop', self.cleanup)
        
    #==========================================================================
    # CherryPy Engine Setup / Cleanup
    #==========================================================================
    def setup( self ):
        '''
        Called on CherryPy engine start.
        '''
        
        self.db = Database()
        self.db.connect( self.db_name )
    
    def cleanup( self ):
        '''
        Called on CherryPy engine stop.
        '''
        
        return
    
    #==========================================================================
    # Web Server Helpers
    #==========================================================================
    def package_images( self, imgtups ):
        '''
        Convert a list of tuples from the DB (camid, timestamp) to a list of 
        URLs that will point to the images (thumbnails by default).
        '''
        
        imgs = []
        for camid, timestamp in imgtups:
                imgs.append( 'image?camid={0}&timestamp={1}'.format( camid, timestamp ) )
                
        return imgs
    
    def get_image( self, camid, timestamp, dbfunc ):
        '''
        Returns the binary image data for the provided camid and timestamp 
        using the provided dbfunc to get the image path.
        '''
        
        if timestamp == None or timestamp == '':
            return cherrypy.NotFound
        
        imgpair = dbfunc( camid, timestamp )
        
        if imgpair == None:
            return cherrypy.NotFound
        
        typ, path = imgpair
        
        f = open( path, 'rb' )
        b = f.read()
        f.close()
        
        cherrypy.response.headers['Content-Type'] = typ
        return b
    
    #==========================================================================
    # CherryPy HTTP/URL Handlers
    #==========================================================================
    @cherrypy.expose
    def index( self ):
        '''
        /
        
        Serves the main HTML page for web access.
        '''
        
        f = open( Utils.get_absolute_path( 'templates/index.html' ), 'r' )
        html = f.read()
        f.close()
        
        return html
    
    @cherrypy.expose
    @Utils.jsonp
    def recentimages( self, camid=None, limit=10 ):
        '''
        /recentimages?camid=X&limit=Y 
        
        Get the most recent images, up to the specified limit, only for the 
        specified camid if one is provided.
        '''
        
        try:
            if camid == None or camid == '':
                imgtups = self.db.get_most_recent_images( limit )
            else:
                imgtups = self.db.get_most_recent_images_for_camid( camid, limit )

            return { 'imgurls' : self.package_images( imgtups ) } 
        except:
            return { 'imgurls' : [] }
    
    @cherrypy.expose
    @Utils.jsonp
    def availableimages( self, camid=None, start=None, end=None ):
        '''
        /availableimages?camid=X&start=Y&end=Z
        
        Get the images within the provided range, only for the specified camid 
        is one is provided.
        '''
        
        if start == None or start == '':
            start = Utils.timestamp_datetime_to_str( datetime( 1970, 1, 1, ) )
            
        if end == None or end == '':
            end = Utils.timestamp_datetime_to_str( datetime.now() )
        
        try:
            if camid == None or camid == '':
                imgtups = self.db.get_images_for_range( start, end )
            else:
                imgtups = self.db.get_images_for_range_camid( camid, start, end )
            
            return { 'imgurls' : self.package_images( imgtups ) }
        except:
            return { 'imgurls' : [] }
    
    @cherrypy.expose
    def image( self, camid=0, timestamp=None, size="t" ):
        '''
        /image?camid=X&timestamp=Y
        
        Returns the image data for a given camid, timestamp and size.
        '''

        if size == "f":
            return self.get_image( camid, timestamp, self.db.get_full_path_for_image )
        else:
            return self.get_image( camid, timestamp, self.db.get_thumb_path_for_image )