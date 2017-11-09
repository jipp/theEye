#!/usr/bin/env python

import ConfigParser
import glob
import os


config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')


LOCK_FILE = config.get('path', 'lock_file')
GALLERY = config.get('path', 'gallery')
BROKER_ADDRESS = config.get('mqtt', 'broker_address')
USERNAME = config.get('mqtt', 'username')
PASSWORD = config.get('mqtt', 'password')
NODE = config.get('mqtt', 'nodes')
TOPIC = config.get('mqtt', 'topic')
PARAMETER = config.get('camera', 'parameter')
GALLERY_LINK = config.get('html', 'gallery_link')


def getLastFile():
   os.chdir(GALLERY)
   list_of_files = glob.glob('*.jpg')
   latest_file = max(list_of_files, key=os.path.getctime)
   return latest_file


def header():
   print '''\
<html>
   <meta http-equiv="refresh" content="5">
   <head><title>theEye</title></head>
   <body>
   '''

def footer():
   print '''\
   </body>
</html>
   '''

def site():
   print '''\
      <p><a href="{GALLERY_LINK}">Gallery</a></p>
      <p><img src="{GALLERY_LINK}/{LAST_FILE}" alt="{GALLERY_LINK}/{LAST_FILE}" width="320"></p>
   '''.format(GALLERY_LINK=GALLERY_LINK, LAST_FILE=getLastFile())


def main():
   header()
   site()
   footer()
   getLastFile()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      sys.exit('interrupted')
      pass

