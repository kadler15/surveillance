'''
webserver.py:

Web server providing basic access to content captured
by network cameras through a web interface.
'''

import json
import mimetypes

from server import Server, ServerHandler
from utils import Utils
    
class WebHandler(ServerHandler):
    '''
    HTTP handler class
    '''
    
    # The MIME types associated with this project that we know for sure
    # need to be opened as text files.
    def get_text_mime_types( self ):
        return ['text/css',
                'text/html',  
                'text/javascript',
                'text/plain',
                'text/xml',
                'application/javascript',
                'application/json',
                'application/jsonp',]
    
    def get_GET_handlers( self ):
        return [('^/available-images$', self.GET_available_images),
                ('^/images/.*',         self.GET_image),
                ('^/(index\.html)?$',   self.GET_index),
                ('^/.*',                self.GET_base),]
        
    def GET_available_images( self, parse_result, qs_dict ):
        '''
        available-images handler
        '''
        
        # Get start and end indexes from query
        start = int( qs_dict['start'][0] )
        end = int( qs_dict['end'][0] )
        
        # Generate a list of image URLs
        img_urls = []
        for i in range( start, end + 1 ):
            img_urls.append( '/images/{0}.jpg'.format( i ) )
        
        # Create a dict to run through json.dumps and wrap it with the callback
        json_dict = { 'imgurls' : img_urls }
        json_str = json.dumps( json_dict )
        jsonp_str = '{0}({1})'.format( qs_dict['callback'][0], json_str )
        
        self.send_json_str_response( jsonp_str )
    
    def GET_image( self, parse_result, qs_dict ):
        '''
        Image file access handler
        '''
        
        img_name = parse_result.path[len( '/images/' ):]
        path = Utils.get_absolute_path( 'images/{0}'.format( img_name ) )
        typ, _ =  mimetypes.guess_type( path )
        
        f = open( path, 'rb' )
        b = f.read()
        f.close()
        
        self.send_response_data( typ, b )
    
    def GET_index( self, parse_result, qs_dict ):
        '''
        index.html handler
        '''
        
        f = open( Utils.get_absolute_path( 'templates/index.html' ), 'r' )
        html = f.read()
        f.close()
        
        self.send_response_data( 'text/html', html )
        
    def GET_base( self, parse_result, qs_dict ):
        '''
        Base URL (/) handler
        '''
        
        path = Utils.get_absolute_path( 'static/' + parse_result.path[1:] )
        typ, _ =  mimetypes.guess_type( path )
        
        mode = 'r' if typ in self.get_text_mime_types() else 'rb'
        f = open( path, mode )
        data = f.read()
        f.close()
            
        self.send_response_data( type, data ) 

class WebServer(Server):
    '''
    Surveillance web server
    '''
    
    @classmethod
    def get_handler_class( cls ):
        return WebHandler