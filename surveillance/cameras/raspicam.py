'''
raspicam.py:

Camera class for the Raspberry Pi camera board. Uses the picamera module to
take JPEG images from the camera board.
'''

import io
import picamera

from camera import Camera
from datetime import datetime, timedelta

class Raspicam(Camera):
    def enable( self ):
        self.stream = io.BytesIO()
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1280, 960)
        self.camera.start_preview()
        self.start_time = datetime.now()
        
    def is_ready( self ):
        return datetime.now() - self.start_time > timedelta( seconds=2 )
    
    def rotation( self ):
        return 180
        
    def get_image( self ):
        self.stream.seek(0)
        self.stream.truncate()
        
        self.camera.capture( self.stream, 'jpeg' )
        
        return self.stream.getvalue()