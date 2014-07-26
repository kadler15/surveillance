'''
surveillance_server.py:

Main program for surveillance server.
'''

import cherrypy

from surveillance.utils import Utils
from surveillance.server import Server

def main(): 
    cherrypy.config.update({'server.socket_port' : 8080})
    
    hostmap = {
               '127.0.0.1:8080' : '/webserver',
               'localhost:8080' : '/webserver',
               
               '127.0.0.1:8081' : '/mediaserver',
               'localhost:8081' : '/mediaserver'
               }
    
    # Configure cherrypy to server a static directory and to do
    # virtual routing of 8080 -> webserver, 8081 -> mediaserver.
    conf = {
            '/' :
            {
             'request.dispatch' : cherrypy.dispatch.VirtualHost(**hostmap),
             },
            '/webserver' :
            {
            'tools.sessions.on' : True,
             'tools.staticdir.root' : Utils.get_absolute_path( 'static/' ),
             },
            '/webserver/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './public'
             }
            }
    
    # Start up the second port
    media_server = cherrypy._cpserver.Server()
    media_server.socket_port = 8081
    media_server.subscribe()
    
    # Start up the main port and server
    cherrypy.quickstart(Server( 'surveillance.db' ), '/', conf )
  
if __name__ == '__main__':
    main()