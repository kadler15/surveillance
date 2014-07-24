'''
mediaserver.py:

Media server used by network cameras to off-load
their media content to a central location.
'''

import datetime
import json

from server import Server, ServerHandler
from database import Database

class MediaHandler(ServerHandler):
    '''
    Media server handler class.
    '''
    
    def get_GET_handlers( self ):
        return [('^/ready$',        self.GET_server_ready),]
        
    def get_POST_handlers( self ):
        return [('^/register$',     self.POST_camera_register),
                ('^/upload/image$', self.POST_upload_image),]
    
    def GET_server_ready( self, parse_result, qs_dict ):
        db = Database.get_instance()
        
        json_dict = { 'ready' : db.is_ready(), }
        self.send_json_dict_response( json_dict )
    
    def POST_camera_register( self, parse_result, qs_dict ):
        '''
        Camera registration handler.
        '''
        
        content_type, content_length = self.extract_header_info();
        
        if content_type == 'application/json':
            json_str = self.rfile.read( int( content_length ) )
            json_dict = json.loads( json_str )
                
            db = Database.get_instance()
            camera_id = db.get_camera_id_for_desc( json_dict['desc'] )
            
            if camera_id == None:
                camera_id = db.insert_camera( json_dict['desc'] )
            
            json_dict = { 'camera_id' : id }
            self.send_json_dict_response( json_dict )
        
    def POST_upload_image( self, parse_result, qs_dict ):
        '''
        Image upload handler.
        '''
        
        content_type, content_length = self.extract_header_info();
        
        if content_type == 'image/jpeg':
            img = self.rfile.read( int( content_length ) )
            
            timestamp = datetime.datetime.now()
            timestr = timestamp.strftime( '%Y%m%d %H%M%S%f')
            path = 'images/{0}.jpg'.format( timestr )
            f = open( path, 'wb' )
            f.write( img )
            f.close()
            
            db = Database.get_instance()
            image_id = db.insert_image( int( qs_dict['camera_id'][0] ), 'jpg', path, path, timestamp )
            
            print db.get_most_recent_thumbs(20)
            
            json_dict = { 'image_id' : image_id, }
            self.send_json_dict_response( json_dict )
            
class MediaServer(Server):
    '''
    Media server.
    '''
    
    @classmethod
    def custom_start(cls):
        db = Database.get_instance()
        db.connect('surveillance.db')
        
    @classmethod
    def get_handler_class(cls):
        return MediaHandler