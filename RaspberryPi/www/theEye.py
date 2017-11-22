#!/usr/bin/env python

import ConfigParser
import glob
import os


config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')


LOCAL_GALLERY_FOLDER = config.get('local', 'gallery_folder')
HTML_GALLERY_LINK = config.get('html', 'gallery_link')


def getLastFile():
   os.chdir(LOCAL_GALLERY_FOLDER)
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
      <p><a href="{HTML_GALLERY_LINK}">Gallery</a></p>
      <p><img src="{HTML_GALLERY_LINK}/{LAST_FILE}" alt="{HTML_GALLERY_LINK}/{LAST_FILE}" width="320"></p>
   '''.format(HTML_GALLERY_LINK=HTML_GALLERY_LINK, LAST_FILE=getLastFile())


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
