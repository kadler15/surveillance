'''
server.py:

CherryPy virtual host base server class that instantiates the media and web
servers.
'''

from mediaserver import MediaServer
from webserver import WebServer

class Server(object):
    '''
    Base server to support virtual dispatching.
    '''
    
    def __init__( self, db_name ):
        self.mediaserver = MediaServer( db_name )
        self.webserver = WebServer( db_name )