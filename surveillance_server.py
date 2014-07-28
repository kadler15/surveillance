'''
surveillance_server.py:

Main program for the surveillance server. Starts the CherryPy web engine and
starts the media and web servers.
'''

import cherrypy

from surveillance.utils import Utils
from surveillance.server import Server

#==========================================================================
# Configuration
#==========================================================================
server_ip = '192.168.2.47'
web_port = 8080
media_port = 8081
web_static_dir_root = Utils.get_absolute_path( 'static/' )
web_static_dir_public = './public'
database = 'surveillance.db'

def main(): 
    cherrypy.config.update({'server.socket_host' : server_ip,
                            'server.socket_port' : web_port})
     
    hostmap = {
               '{0}:{1}'.format(server_ip, web_port) : '/webserver',
               '{0}:{1}'.format(server_ip, media_port) : '/mediaserver',
               }
    
    # Configure CherryPy for virtual host and static content.
    conf = {
            '/' :
            {
             'request.dispatch' : cherrypy.dispatch.VirtualHost(**hostmap),
             },
            '/webserver' :
            {
            'tools.sessions.on' : True,
             'tools.staticdir.root' : web_static_dir_root,
             },
            '/webserver/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': web_static_dir_public
             }
            }
    
    # Start up the second port
    media_server = cherrypy._cpserver.Server()
    media_server.socket_host = server_ip
    media_server.socket_port = media_port
    media_server.subscribe()
    
    # Start up the main port and server
    cherrypy.quickstart( Server( database ), '/', conf )
  
if __name__ == '__main__':
    main()