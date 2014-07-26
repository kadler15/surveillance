import cherrypy
import json

from database import Database
from datetime import datetime
from utils import Utils

def jsonp( func ):
    '''
    Handler for cherrypy to wrap json responses with proper
    callback if a cherrypy method is decorated with @jsonp.
    '''
    
    def handle_callback( self, *args, **kwargs ):
        callback, _ = None, None
        if 'callback' in kwargs and '_' in kwargs:
            callback, _ = kwargs['callback'], kwargs['_']
            del kwargs['callback'], kwargs['_']
        ret = func( self, *args, **kwargs )
        if callback is not None:
            ret = '%s(%s)' % (callback, json.dumps( ret ))
        return ret
    return handle_callback

class WebServer(object):
    '''
    Web server for external web clients to access archived imagery.
    '''
    
    def __init__( self, db_name ):
        self.db_name = db_name
        self.database = None
        
    def db( self ):
        if self.database == None:
            self.database = Database()
            self.database.connect( self.db_name )
            
        return self.database
    
    def package_thumbs( self, imgtups ):
        '''
        Convert a list of tuples from the DB (camid, timestamp) to
        a list of URLs that will point to the thumbnails.
        '''
        
        imgs = []
        for camid, timestamp in imgtups:
                imgs.append( 'thumb?camid={0}&timestamp={1}'.format( camid, timestamp ) )
                
        return imgs
    
    def image( self, camid, timestamp, dbfunc ):
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
    @jsonp
    def recentimages( self, camid=None, limit=10 ):
        '''
        /recentimages?camid=X&limit=Y 
        
        Get the most recent images, up to the specified limit,
        only for the specified camid if one is provided.
        '''
        
        try:
            if camid == None or camid == '':
                imgtups = self.db().get_most_recent_images( limit )
            else:
                imgtups = self.db().get_most_recent_images_for_camid( camid, limit )

            return { 'imgurls' : self.package_thumbs( imgtups ) } 
        except:
            return { 'imgurls' : [] }
    
    @cherrypy.expose
    @jsonp
    def availableimages( self, camid=None, start=None, end=None ):
        '''
        /availableimages?camid=X&start=Y&end=Z
        
        Get the images within the provided range, only
        for the specified camid is one is provided.
        '''
        
        if start == None or start == '':
            start = Utils.timestamp_datetime_to_str( datetime( 1970, 1, 1, ) )
            
        if end == None or end == '':
            end = Utils.timestamp_datetime_to_str( datetime.now() )
        
        try:
            if camid == None or camid == '':
                imgtups = self.db().get_images_for_range( start, end )
            else:
                imgtups = self.db().get_images_for_range_camid( camid, start, end )
            
            return { 'imgurls' : self.package_thumbs( imgtups ) }
        except:
            return { 'imgurls' : [] }
    
    @cherrypy.expose
    def thumb( self, camid=0, timestamp=None ):
        '''
        /thumb?camid=X&timestamp=Y
        
        Returns the binary thumbnail data for a given camid and timestamp.
        '''
        
        return self.image( camid, timestamp, self.db().get_thumb_path_for_image )
    
    @cherrypy.expose    
    def full( self, camid=0, timestamp=None ):
        '''
        /full?camid=X&timestamp=Y
        
        Returns the binary full image data for a given camid and timestamp.
        '''
        
        return self.image( camid, timestamp, self.db().get_full_path_for_image )