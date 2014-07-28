'''
utils.py:

Utility methods.
'''

import Image
import os
import errno
import json

from datetime import datetime

class Utils():
    '''
    Utility class
    '''
    
    #==========================================================================
    # IO Methods
    #==========================================================================
    @classmethod 
    def get_absolute_path( cls, relative_path ):
        '''
        Get an absolute file path for a relative file path. The absolute path 
        is based on the script directory.
        '''
        
        script_dir = os.path.dirname( os.path.realpath(__file__) )
        return os.path.join( script_dir, relative_path )
    
    @classmethod
    def make_sure_path_exists(cls, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    #==========================================================================
    # Web Methods
    #==========================================================================
    @classmethod
    def jsonp( cls, func ):
        '''
        Handler for cherrypy to wrap json responses with proper callback if a 
        cherrypy method is decorated with @jsonp.
        '''
    
        def handle_callback( self, *args, **kwargs ):
            callback, _ = None, None
            if 'callback' in kwargs and '_' in kwargs:
                callback, _ = kwargs['callback'], kwargs['_']
                del kwargs['callback'], kwargs['_']
            ret = func( self, *args, **kwargs )
            if callback is not None:
                ret = '%s(%s)' % (callback, json.dumps( ret ))
            return ret
        return handle_callback
    
    #==========================================================================
    # Timestamp Methods
    #==========================================================================
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
    
    #==========================================================================
    # Image Processing Methods
    #==========================================================================
    @classmethod
    def process_image( cls, camid, timestamp, raw_full, rotate ):
        try:
            cls.make_sure_path_exists( 'full/' )
            cls.make_sure_path_exists( 'thumb/' )
        except:
            return cls.process_image( camid, timestamp, raw_full )
        
        full_path = 'full/{0}_{1}.jpg'.format( camid, timestamp )
        thumb_path = 'thumb/{0}_{1}.jpg'.format( camid, timestamp )
        
        # Write the full image to disk
        f = open( full_path, 'wb' )
        f.write( raw_full )
        f.close()
        
        # Open the full image in PIL
        thumb_size = 256, 256
        full = Image.open( full_path )
        
        try:
            rotate = int( rotate )
        except:
            rotate = -1
        
        if rotate > 0 and rotate < 360:
            full = full.rotate( rotate )
            full.save( full_path )
        
        full.thumbnail( thumb_size, Image.ANTIALIAS )
        full.save( thumb_path )
            
        return (full_path, thumb_path)