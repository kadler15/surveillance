'''
basic_simulated_camera.py:

A very basic camera simulator that returns sample images contained in the
surveillance project images/ folder.
'''

from surveillance.utils import Utils
from camera import Camera

class BasicSimulatorCamera(Camera):
    def __init__( self ):
        super( BasicSimulatorCamera, self ).__init__()
        
        self.image_idx = 1
        
    def enable( self ):
        pass
    
    def is_ready( self ):
        return True
    
    def get_image( self ):
        '''
        Loop through each of the sample images, returning one image on each 
        call and advancing for the next call.
        '''
        
        path = Utils.get_absolute_path( 'images/{0}.jpg'.format( self.image_idx ) )
        self.increment_idx()
        
        f = open( path, 'rb' )
        b = f.read()
        f.close()
        
        return b
    
    def increment_idx( self ):
        self.image_idx = 1 if self.image_idx == 8 else self.image_idx + 1