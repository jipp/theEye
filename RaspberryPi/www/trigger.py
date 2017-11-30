#!/usr/bin/env python

import paho.mqtt.publish as publish
import ConfigParser
import sys
import platform


id = platform.node()
config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')

try:
   mqtt_host = config.get('mqtt', 'host')
   mqtt_username = config.get('mqtt', 'username')
   mqtt_password = config.get('mqtt', 'password')
except Exception as e:
   print(e)
   sys.exit('interrupted')


def redirect():
   print '''\
<html>
   <meta http-equiv="refresh" content="1;url=theEye.py">
   <head><title>theEye</title></head>
   <body>
      take photo ...
   </body>
</html>
   '''


def main():
   publish.single(id + "/value", "{\"manual\":true}", hostname = mqtt_host, auth = {'username': mqtt_username, 'password': mqtt_password})
   redirect()

if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      sys.exit('interrupted')
