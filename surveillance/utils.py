'''
utils.py:

Utility methods.
'''

import os

from datetime import datetime

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
        
        script_dir = os.path.dirname( os.path.realpath(__file__) )
        return os.path.join( script_dir, relative_path )
    
    time_format = '%Y%m%d%H%M%S%f'
    
    @classmethod
    def timestamp_str_to_datetime( cls, timestamp ):
        return datetime.strptime( timestamp, cls.time_format )
    
    @classmethod
    def timestamp_datetime_to_str( cls, timestamp ):
        return datetime.strftime( timestamp, cls.time_format )
    
    @classmethod
    def timestamp_now_datetime( cls ):
        return datetime.now()
    
    @classmethod
    def timestamp_now_str( cls ):
        return cls.timestamp_datetime_to_str( cls.timestamp_now_datetime() )