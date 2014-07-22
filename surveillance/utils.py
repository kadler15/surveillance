'''
utils.py:

Utility methods.
'''

import os

class Utils():
    '''
    Utility class
    '''
    
    @classmethod 
    def get_absolute_path( cls, relative_path ):
        '''
        Get an absolute file path for a relative file path.
        The absolute path is based on the script directory.
        '''
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join( script_dir, relative_path )