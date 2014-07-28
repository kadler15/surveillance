'''
surveillance_client.py:

Main program for surveillance clients. Starts a media client that captures
images and sends the images to the network media server.
'''

from surveillance.cameras.raspicam import Raspicam
from surveillance.mediaclient import MediaClient

#==========================================================================
# Configuration
#==========================================================================
server_url = 'http://192.168.2.47'
server_port = 8081
camera = Raspicam()
desc = 'Test Camera'

def main():
    MediaClient().start( server_url, server_port, camera, desc )
  
if __name__ == '__main__':
    main()