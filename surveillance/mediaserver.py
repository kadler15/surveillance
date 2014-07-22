'''
mediaserver.py:

Media server used by network cameras to off-load
their media content to a central location.
'''

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

import cgi
import json

class MediaHandler(BaseHTTPRequestHandler):
    # Unique image index
    image_idx = -1
          
    def do_GET(self):
        '''
        Media server GET handler for server alive verification.
        '''
        
        json_dict = { 'alive' : 1 }
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
        
        # Parse out the content type and length from the headers
        content_type, _ = cgi.parse_header( self.headers.getheader( 'Content-Type' ) )
        content_length, _ = cgi.parse_header( self.headers.getheader( 'Content-Length' ) )
        
        if content_type == 'image/jpeg':
            # We can do self.rfile.read() here based on the length
            
            # Tick the unique image index and form the JSON response
            # to inform the client of the unique ID assigned to the image.
            # This unique increment will need to be thread safe.
            MediaHandler.image_idx += 1
            json_dict = { 'imgid' : MediaHandler.image_idx, }
            json_str = json.dumps( json_dict )
            
            self.send_response( 200 )
            self.send_header( 'Content-Type', 'application/json' )
            self.send_header('Content-Length', len( json_str ) )
            self.end_headers()
        
            # Send out the JSON response
            self.wfile.write( json_str )

class MediaServer(ThreadingMixIn, HTTPServer):
    '''
    Media server.
    '''
    
    @classmethod
    def start(cls, servers, port):
        server_address = ('localhost', port)
        httpd = HTTPServer( server_address, MediaHandler )
        servers.append( httpd )
        httpd.serve_forever()