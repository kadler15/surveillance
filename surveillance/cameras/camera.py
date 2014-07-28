'''
camera.py:

The base camera class.
'''

class Camera(object):
    '''
    The base class for all Cameras.
    '''
    
    def enable( self ):
        '''
        Prepare the camera for use.
        '''
        
        return None
        
    def is_ready( self ):
        '''
        Is the camera ready to take images?
        '''
        
        return None
    
    def rotation( self ):
        '''
        How many degrees should the server rotate the images being sent by the 
        camera?
        '''
        
        return 0
    
    def get_image( self ):
        '''
        Get the binary data for a single image file.
        '''
        
        return None