'''
mediaclient.py:

Media client for the network cameras to send
image data to the media server.
'''

import urllib2
import time
import json

from cameras.basic_simulator import BasicSimulatorCamera

class MediaClient():
    '''
    Media client for internal cameras to upload images
    to internal media server.
    '''
    
    def __init__( self ):
        self.camid = 0
    
    def wait_server_ready( self, base_url ):
        '''
        Block until the media server indicates it is
        ready to accept clients.
        '''
        
        while( True ):
            req = urllib2.Request( base_url + '/ready' )
            response = urllib2.urlopen( req )
            content_type = response.info().getheader( 'Content-Type' )
            content_length = response.info().getheader( 'Content-Length' )
            
            if content_type == 'application/json':
                json_str = response.read( int( content_length ) )
                json_dict = json.loads( json_str )
                
                if json_dict['ready']:
                    break
                
            time.sleep( 5 )
            
    def register_camera( self, desc, base_url ):
        '''
        Register the client with the media server.
        '''
        
        json_dict = { 'desc' : desc, }
        json_str = json.dumps( json_dict )
        
        url = base_url + '/register'
        req = urllib2.Request( url )
        req.add_header( 'Content-Type', 'application/json' )
        req.add_header( 'Content-length', '{0}'.format( len( json_str ) ) )
        req.add_data( json_str )
        
        response = urllib2.urlopen( req )
        content_type = response.info().getheader( 'Content-Type' )
        content_length = response.info().getheader( 'Content-Length' )
            
        if content_type == 'application/json':
            json_str = response.read( int( content_length ) )
            json_dict = json.loads( json_str )
            self.camid = json_dict['camid']
            
    def send_image( self, camera, base_url ):
        '''
        Send an image to the media server.
        '''
        
        img = camera.get_image()
            
        url = base_url + '/upload?camid={0}'.format( self.camid )
        req = urllib2.Request( url, img )
        req.add_header( 'Cache-Control', 'no-cache' )
        req.add_header( 'Content-Type', 'image/jpeg' )
        req.add_header( 'Content-Length', '{0}'.format( len( img ) ) )
            
        response = urllib2.urlopen( req )
        content_type = response.info().getheader( 'Content-Type' )
        content_length = response.info().getheader( 'Content-Length' )
            
        if content_type == 'application/json':
            json_str = response.read( int( content_length ) )
            print json_str
    
    def start( self, server, port, desc ):
        '''
        Start the media client and connect to the server
        at the specified port.
        '''
        
        camera = BasicSimulatorCamera()
        base_url = '{0}:{1}'.format( server, port )
        
        self.wait_server_ready( base_url )
        self.register_camera( desc, base_url )
        
        while( True ):
            self.send_image(camera, base_url)
            
            time.sleep(5)