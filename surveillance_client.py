'''
surveillance_client.py:

Main program for surveillance client.
'''

from surveillance.mediaclient import MediaClient

def main():
    MediaClient().start( 'http://127.0.0.1', 8081, 'Test Camera' )
  
if __name__ == '__main__':
    main()