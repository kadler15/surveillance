'''
raspi-surveillance.py:

Web server providing basic access to content captured
by Raspberry Pi Camera.
'''

import json
import os
import mimetypes

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs

class WebAPI(object):
    '''
    Various classmethods to handle URL parsing and generating
    proper HTTP response headers and data.
    '''
    
    # The path strings for parsing.
    path_available_images  = '/available-images.json'
    path_get_image         = '/images/'
    path_index             = '/index.html'
    path_base              = '/'
    
    # The MIME types associated with this project that we know for sure
    # need to be opened as text files.
    text_mime_types = [
                       'text/css',
                       'text/html',  
                       'text/javascript',
                       'text/plain',
                       'text/xml',
                       'application/javascript',
                       'application/json',
                       'application/jsonp',
                       ]

    @classmethod
    def dispatch(cls, full_path):
        '''
        Route a URL to the appropriate handler.
        '''
        
        # Parse the URL and get the query dict
        parse_result = urlparse(full_path)
        qs_dict = parse_qs(parse_result.query)
         
        # get_available_images
        if parse_result.path == cls.path_available_images:
            return cls.get_available_images( qs_dict )

        # get_image
        elif parse_result.path.startswith( cls.path_get_image ):
            img_name = parse_result.path[len( cls.path_get_image ):]
            return cls.get_image( img_name )
        
        # get_index
        elif parse_result.path == cls.path_index or parse_result.path == cls.path_base:
            return cls.get_index()
        
        # get_base
        elif parse_result.path.startswith( cls.path_base ):
            path = parse_result.path[len( cls.path_base ):]
            return cls.get_base( path )
    
    @classmethod
    def get_available_images( cls, qs_dict ):
        '''
        available-images.json handler
        '''
        
        # Get start and end indexes from query
        start = int( qs_dict['start'][0] )
        end = int( qs_dict['end'][0] )
        
        # Generate a list of image URLs
        img_urls = []
        for i in range( start, end + 1 ):
            img_urls.append( cls.path_get_image + '{0}.jpg'.format( i ) )
        
        # Create a dict to run through json.dumps and wrap it with the callback
        json_dict = { 'imgurls' : img_urls }
        json_str = json.dumps( json_dict )
        jsonp_str = '{0}({1})'.format( qs_dict['callback'][0], json_str )
        
        return { 
               'type' : 'application/json', 
               'data' : jsonp_str,
               }
    
    @classmethod
    def get_image( cls, img_name ):
        '''
        Image file access handler
        '''
        
        path = Utils.get_absolute_path( 'images/{0}'.format( img_name ) )
        type, encoding =  mimetypes.guess_type( path )
        
        f = open( path, 'rb' )
        bin = f.read()
        f.close()
        
        return { 
                'type' : type, 
                'data' : bin,
                }
    
    @classmethod
    def get_index( cls ):
        '''
        index.html handler
        '''
        
        # 
        f = open( Utils.get_absolute_path( 'templates/index.html' ), 'r' )
        html = f.read()
        f.close()
        
        return {
                'type' : 'text/html',
                'data' : html,
                }
        
    @classmethod
    def get_base( cls, path ):
        '''
        Base URL (/) handler
        '''
        
        path = Utils.get_absolute_path( 'static/' + path )
        type, encoding =  mimetypes.guess_type( path )
        
        mode = 'r' if type in cls.text_mime_types else 'rb'
        f = open( path, mode )
        text = f.read()
        f.close()
            
        return {
                'type' : type,
                'data' : text,
                }
    
class HttpHandler(BaseHTTPRequestHandler):
    '''
    HTTP handler class
    '''
    
    def do_GET(self):
        try:
            api_output = WebAPI.dispatch( self.path )
            if api_output == None:
                raise Exception()

            self.send_response( 200 )

            self.send_header( 'Content-Type', api_output['type'] )
            self.end_headers()
            
            self.wfile.write(api_output['data'])
            return
        
        except:
            self.send_error(404, 'error')
            
class Utils():
    '''
    Utility class
    '''
    
    @classmethod 
    def get_absolute_path( cls, relative_path ):
        '''
        Get an absolute file path for a relative file path.
        The absolute path is based on the script directory.
        '''
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join( script_dir, relative_path ) 

def main():
    server_address = ('localhost', 8080)
    httpd = HTTPServer( server_address, HttpHandler )
    httpd.serve_forever()
  
if __name__ == '__main__':
    main()