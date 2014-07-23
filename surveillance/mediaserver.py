'''
mediaserver.py:

Media server used by network cameras to off-load
their media content to a central location.
'''

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from urlparse import urlparse, parse_qs
from database import Database

import cgi
import datetime
import json

class MediaApi(object):
    '''
    Various classmethods to handle URL parsing and generating
    proper HTTP response headers and data.
    '''
    
    # The path strings for parsing.
    path_upload_image    = '/upload/image'
    path_register_camera = '/register'
    
    @classmethod
    def dispatch(cls, full_path, media_handler):
        '''
        Route a URL to the appropriate handler.
        '''
        
        # Parse the URL and get the query dict
        parse_result = urlparse(full_path)
        qs_dict = parse_qs(parse_result.query)
         
        # get_available_images
        if parse_result.path == cls.path_upload_image:
            return cls.upload_image( qs_dict )

class MediaHandler(BaseHTTPRequestHandler):
    '''
    Media server handler class.
    '''
    
    # The path strings for parsing.
    path_upload_image  = '/upload/image'
    path_camera_register = '/register'
    
    def do_GET(self):
        '''
        Media server GET handler for server ready verification.
        '''
        
        db = Database.get_instance()
        
        json_dict = { 'ready' : db.is_ready(), }
        json_str = json.dumps( json_dict )
        
        self.send_response( 200 )
        
        self.send_header( 'Content-Type', 'application/json' )
        self.send_header( 'Content-Length', len( json_str ) )
        self.end_headers()
        
        self.wfile.write( json_str )
    
    def do_POST(self):
        '''
        Media server POST handler.
        '''
        
        # Parse the URL and get the query dict
        parse_result = urlparse(self.path)
        qs_dict = parse_qs(parse_result.query)
        
        if parse_result.path == self.path_camera_register:
            self.camera_register()
        elif parse_result.path == self.path_upload_image:
            self.upload_image( qs_dict )
            
    def camera_register(self):
        # Parse out the content type and length from the headers
        content_type, _ = cgi.parse_header( self.headers.getheader( 'Content-Type' ) )
        content_length, _ = cgi.parse_header( self.headers.getheader( 'Content-Length' ) )
        
        if content_type == 'application/json':
            json_str = self.rfile.read( int( content_length ) )
            json_dict = json.loads(json_str)
                
            db = Database.get_instance()
            camera_id = db.get_camera_id_for_desc(json_dict['desc'])
            
            if camera_id == None:
                camera_id = db.insert_camera(json_dict['desc'])
            
            json_dict = { 'camera_id' : id }
            json_str = json.dumps( json_dict )
            
            self.send_response( 200 )
            self.send_header( 'Content-Type', 'application/json' )
            self.send_header( 'Content-Length', len( json_str ) )
            self.end_headers()
            
            self.wfile.write( json_str )
        
    def upload_image(self, qs_dict ):
        # Parse out the content type and length from the headers
        content_type, _ = cgi.parse_header( self.headers.getheader( 'Content-Type' ) )
        content_length, _ = cgi.parse_header( self.headers.getheader( 'Content-Length' ) )
        
        if content_type == 'image/jpeg':
            img = self.rfile.read( int( content_length ) )
            
            timestamp = datetime.datetime.now()
            timestr = timestamp.strftime( '%Y%m%d %H%M%S%f')
            path = 'images/{0}.jpg'.format( timestr )
            f = open( path, 'wb' )
            f.write(img)
            f.close()
            
            db = Database.get_instance()
            image_id = db.insert_image( int( qs_dict['camera_id'][0] ), 'jpg', path, path, timestamp )
            
            print db.get_most_recent_thumbs(20)
            
            json_dict = { 'image_id' : image_id, }
            json_str = json.dumps( json_dict )
            
            self.send_response( 200 )
            self.send_header( 'Content-Type', 'application/json' )
            self.send_header( 'Content-Length', len( json_str ) )
            self.end_headers()
        
            # Send out the JSON response
            self.wfile.write( json_str )
            
class MediaServer(ThreadingMixIn, HTTPServer):
    '''
    Media server.
    '''
    
    @classmethod
    def start(cls, servers, port):
        db = Database.get_instance()
        db.connect('surveillance.db')
        
        server_address = ('localhost', port)
        httpd = HTTPServer( server_address, MediaHandler )
        servers.append( httpd )
        httpd.serve_forever()