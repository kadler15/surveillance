'''
server.py:

Base server class.
'''

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from urlparse import urlparse, parse_qs

import cgi
import json
import re

class ServerHandler(BaseHTTPRequestHandler):
    '''
    Base server handler class.
    '''

    def get_GET_handlers( self ):
        return []
        
    def get_POST_handlers( self ):
        return []
    
    def do_HTTP( self, handlers ):
        parse_result = urlparse( self.path )
        qs_dict = parse_qs( parse_result.query )
        
        for urlregex, handler in handlers:
            if re.match( urlregex, parse_result.path ):
                return handler( parse_result, qs_dict ) 
            
        self.send_response( 404, 'Error' )
    
    def do_GET( self ):
        '''
        Server GET handler.
        '''
        
        self.do_HTTP( self.get_GET_handlers() )
    
    def do_POST( self ):
        '''
        Server POST handler.
        '''
        
        self.do_HTTP( self.get_POST_handlers() )
        
    def send_json_dict_response( self, json_dict ):
        json_str = json.dumps( json_dict )
        self.send_json_str_response( json_str )
        
    def send_json_str_response( self, json_str ):
        self.send_response_data( 'application/json', json_str )
        
    def send_response_data( self, typ, data ):
        self.send_response( 200 )
        
        self.send_header( 'Content-Type', typ )
        self.send_header( 'Content-Length', len( data ) )
        self.end_headers()
        
        self.wfile.write( data )
        
    def extract_header_info( self ):
        # Parse out the content type and length from the headers
        content_type, _ = cgi.parse_header( self.headers.getheader( 'Content-Type' ) )
        content_length, _ = cgi.parse_header( self.headers.getheader( 'Content-Length' ) )
        
        return (content_type, content_length)
            
class Server(ThreadingMixIn, HTTPServer):
    '''
    Base server.
    '''
    
    @classmethod
    def custom_start(cls):
        pass
    
    @classmethod
    def get_handler_class(cls):
        return ServerHandler
    
    @classmethod
    def start(cls, servers, port ):
        cls.custom_start()
        
        server_address = ('localhost', port)
        httpd = HTTPServer( server_address, cls.get_handler_class() )
        servers.append( httpd )
        httpd.serve_forever()