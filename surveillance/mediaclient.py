'''
mediaclient.py:

Media client for the network cameras to send
image data to the media server.
'''

import urllib2
import time

from cameras.basic_simulator import BasicSimulatorCamera

class MediaClient():
    '''
    Media client class.
    '''    
    
    @classmethod
    def start(cls, url, port):
        '''
        Start the media client and connect to the server
        at the specified port.
        '''
        
        camera = BasicSimulatorCamera()
        
        while( True ):
            img = camera.get_image()
            
            full_url = '{0}:{1}'.format( url, port )
            req = urllib2.Request(full_url, img)
            req.add_header( 'Cache-Control', 'no-cache' )
            req.add_header( 'Content-Type', 'image/jpeg' )
            req.add_header( 'Content-Length', '{0}'.format( len( img ) ) )
            
            response = urllib2.urlopen( req )
            content_type = response.info().getheader( 'Content-Type' )
            content_length = response.info().getheader( 'Content-Length' )
            
            if content_type == 'application/json':
                json_str = response.read( int( content_length ) )
                print json_str
            
            time.sleep(5)