#!/usr/bin/env python

import ConfigParser
import glob
import os


config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')


local_folder = config.get('local', 'folder')
gallery_link = config.get('gallery', 'link')


def getLastFile():
   os.chdir(local_folder)
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
      <p><a href="{gallery_link}">Gallery</a></p>
      <p><img src="{gallery_link}/{last_file}" alt="{gallery_link}/{last_file}" width="320"></p>
      <form action="trigger.py" method="get">
      <p>take photo: <button type="submit">Now</button>
   '''.format(gallery_link=gallery_link, last_file=getLastFile())


def main():
   header()
   site()
   footer()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      sys.exit('interrupted')
      pass
