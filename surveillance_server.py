'''
surveillance_server.py:

Main program for surveillance server.
'''

import threading
import sys

from surveillance.webserver import WebServer
from surveillance.mediaserver import MediaServer

def main():
    threads = []
    servers = []
    
    t = threading.Thread( target=lambda : WebServer.start( servers, 8080 ) )
    threads.append( t )
    t.start()
    
    t = threading.Thread( target=lambda : MediaServer.start( servers, 8081 ) )
    threads.append( t )
    t.start()
    
    try:
        while( True ):
            pass
    except KeyboardInterrupt:
        for server in servers:
            server.shutdown()
            
        for thread in threads:
            thread.join()
        
        sys.exit()
  
if __name__ == '__main__':
    main()