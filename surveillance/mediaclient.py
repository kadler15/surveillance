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
    Media client class.
    '''
    
    camera_id = 0
    
    @classmethod
    def wait_server_ready(cls, base_url):
        while( True ):
            req = urllib2.Request(base_url)
            response = urllib2.urlopen(req)
            content_type = response.info().getheader( 'Content-Type' )
            content_length = response.info().getheader( 'Content-Length' )
            
            if content_type == 'application/json':
                json_str = response.read( int( content_length ) )
                json_dict = json.loads(json_str)
                
                if json_dict['ready']:
                    break
                
            time.sleep(5)
            
    @classmethod
    def register_camera(cls, desc, base_url):
        json_dict = { 'desc' : desc, }
        json_str = json.dumps( json_dict )
        
        url = base_url + '/register'
        req = urllib2.Request(url)
        req.add_header( 'Content-Type', 'application/json' )
        req.add_header( 'Content-length', '{0}'.format( len( json_str ) ) )
        
        response = urllib2.urlopen( req )
        content_type = response.info().getheader( 'Content-Type' )
        content_length = response.info().getheader( 'Content-Length' )
            
        if content_type == 'application/json':
            json_str = response.read( int( content_length ) )
            json_dict = json.loads( json_str )
            cls.camera_id = json_dict['camera_id']
            
    @classmethod
    def send_image(cls, camera, base_url):
        img = camera.get_image()
            
        url = base_url + '/upload/image?camera_id={0}'.format( cls.camera_id )
        req = urllib2.Request(url, img)
        req.add_header( 'Cache-Control', 'no-cache' )
        req.add_header( 'Content-Type', 'image/jpeg' )
        req.add_header( 'Content-Length', '{0}'.format( len( img ) ) )
            
        response = urllib2.urlopen( req )
        content_type = response.info().getheader( 'Content-Type' )
        content_length = response.info().getheader( 'Content-Length' )
            
        if content_type == 'application/json':
            json_str = response.read( int( content_length ) )
            print json_str
    
    @classmethod
    def start(cls, server, port):
        '''
        Start the media client and connect to the server
        at the specified port.
        '''
        
        camera = BasicSimulatorCamera()
        base_url = '{0}:{1}'.format(server, port)
        
        cls.wait_server_ready(base_url)
        
        while( True ):
            cls.send_image(camera, base_url)
            
            time.sleep(5)