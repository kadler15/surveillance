'''
mediaclient.py:

Media client for the network cameras to send
image data to the media server.
'''

import urllib2
import time
import threading
import json

from Queue import Queue

class MediaClient():
    '''
    Media client for internal cameras to upload images to internal media 
    server.
    '''
    
    def __init__( self ):
        self.camid = 0
    
    #==========================================================================
    # Startup
    #========================================================================== 
    def wait_server_ready( self ):
        '''
        Block until the media server indicates it is ready to accept clients.
        '''
        
        while( True ):
            req = urllib2.Request( self.base_url + '/ready' )
            response = urllib2.urlopen( req )
            content_type = response.info().getheader( 'Content-Type' )
            content_length = response.info().getheader( 'Content-Length' )
            
            if content_type == 'application/json':
                json_str = response.read( int( content_length ) )
                json_dict = json.loads( json_str )
                
                if json_dict['ready']:
                    break
                
            time.sleep( 5 )
            
    def register_camera( self, desc ):
        '''
        Register the client with the media server.
        '''
        
        json_dict = { 'desc' : desc, }
        json_str = json.dumps( json_dict )
        
        url = self.base_url + '/register'
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
            
    #==========================================================================
    # Single Image Send
    #========================================================================== 
    def send_image( self ):
        '''
        Send an image to the media server.
        '''
        
        img = self.camera.get_image()
            
        url = self.base_url + '/upload?camid={0}&rotate={1}'.format( self.camid, self.camera.rotation() )
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
            
    #==========================================================================
    # Multi Image Send
    #========================================================================== 
    def send_images( self, imgs ):
        '''
        Send the queued images to the media server.
        '''
        
        url = self.base_url + '/multiupload?camid={0}&rotate={1}'.format( self.camid, self.camera.rotation() )
        
        total_len = 0
        b = None
        for img_len, img in imgs:
            total_len += img_len
            if b == None:
                b = img
            else:
                b += img
            url += '&length={0}'.format( img_len )
        
        req = urllib2.Request( url, b )
        req.add_header( 'Cache-Control', 'no-cache' )
        req.add_header( 'Content-Type', 'image/jpeg' )
        req.add_header( 'Content-Length', '{0}'.format( total_len ) )
            
        response = urllib2.urlopen( req )
        content_type = response.info().getheader( 'Content-Type' )
        content_length = response.info().getheader( 'Content-Length' )
            
        if content_type == 'application/json':
            json_str = response.read( int( content_length ) )
            print json_str
            
    #==========================================================================
    # Multi Image Threads
    #========================================================================== 
    def net_worker( self ):
        '''
        Method run by the net_worker. Polls the image queue, pulling images
        off, and sending them to the media server in batches.
        '''
        
        while( self.run ):
            size = self.queue.qsize()
            if size > 0:
                imgs = []
                while size > 0:
                    imgs.append( self.queue.get() )
                    size -= 1
                    
                self.send_images( imgs )
    
    def cam_worker( self ):
        '''
        Method run by the cam_worker. Gets images from the camera instance
        and puts them on the image queue.
        '''
        
        while( self.run ):
            img = self.camera.get_image()
            self.queue.put( ( len( img ), img ) )
            time.sleep( 0.1 )
    
    #==========================================================================
    # Start Media Client
    #========================================================================== 
    def start( self, server, port, camera, desc ):
        '''
        Start the media client and connect to the server at the specified port.
        Begin send images using the provided camera.
        '''
        
        self.camera = camera
        self.camera.enable()
        self.base_url = '{0}:{1}'.format( server, port )

        self.wait_server_ready()
        self.register_camera( desc )
        
        while( not self.camera.is_ready() ):
            pass
        
        #self.run = True
        #self.queue = Queue()
        #tcam = threading.Thread( name='cam_worker', target=self.cam_worker)
        #tnet = threading.Thread( name='net_worker', target=self.net_worker)
        
        #tcam.start()
        #tnet.start()
        
        #try:
        #    while( True ):
        #        pass
        #except:
        #    self.run = False
            
        while( True ):
            self.send_image()
            #time.sleep(5)