#!/usr/bin/env python

#apt -y install python-pip
#pip install paho-mqtt
#apt -y python-paramiko

#mosquitto_pub -h theEye -t 5ccf7f3c8da1/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":false,\"pir\":true}"
#mosquitto_pub -h theEye -t 5ccf7f3c8da1/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":true,\"pir\":false}"


import paho.mqtt.client as mqtt
import json
import logging
import time
import os
import sys
import ConfigParser
import paramiko


#logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
logging.getLogger("paramiko.transport").setLevel(logging.INFO)
paramiko.util.log_to_file('/tmp/paramiko.log')


config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')


LOCK_FILE = config.get('path', 'lock_file')
GALLERY = config.get('path', 'gallery')
BROKER_ADDRESS = config.get('mqtt', 'broker_address')
USERNAME = config.get('mqtt', 'username')
PASSWORD = config.get('mqtt', 'password')
NODES = config.get('mqtt', 'nodes').split(',')
TOPIC = config.get('mqtt', 'topic')
COMMAND = config.get('camera', 'command')
PARAMETER = config.get('camera', 'parameter')
ID = config.get('camera', 'id')
EXTENSION = config.get('camera', 'extension')
REMOTE_HOST = config.get('remote', 'host')
REMOTE_ENABLED = config.getboolean('remote', 'enabled')
REMOTE_USERNAME = config.get('remote', 'username')
REMOTE_PASSWORD = config.get('remote', 'password')
REMOTE_FOLDER = config.get('remote', 'remoteFolder')

def createLockFile():
   f = open(LOCK_FILE, "w+")


def checkLockFile():
   return os.path.isfile(LOCK_FILE)


def takePhoto():
   if (not checkLockFile()):
      createLockFile()
      timestr = time.strftime("%Y%m%d-%H%M%S")
      file = "{0}-{1}.{2}".format(ID, timestr, EXTENSION)
      cmd = "{0} {1} {2}{3} 2>&1".format(COMMAND, PARAMETER, GALLERY, file)
      logging.warning(cmd)
      os.system(cmd)
      os.remove(LOCK_FILE)
      if (REMOTE_ENABLED):
         upload(GALLERY, file)
   else:
      logging.warning("takePhoto blocked")

def upload(folder, file):
   localfile = "{0}{1}".format(folder, file)
   remotefile = "{0}{1}".format(REMOTE_FOLDER, file)
   transport = paramiko.Transport((REMOTE_HOST, 22))
   transport.connect(username = REMOTE_USERNAME, password = REMOTE_PASSWORD)
   sftp = paramiko.SFTPClient.from_transport(transport)
   sftp.put(localfile, remotefile)
   sftp.close()
   transport.close()


def on_connect(client, userdata, flags, rc):
   logging.info('rc: ' + str(rc))


def on_message(client, userdata, message):
   dictionary = {}
   logging.info(message.topic + " " + str(message.qos) + " " + str(message.payload))
   payload = json.loads(message.payload)
   node = message.topic.split("/")[0]
   dictionary['button']  = payload['button']
   dictionary['pir']     = payload['pir']
   logging.info('node: ' + node + ', button: ' + str(returnValue(dictionary, 'button')) + ', pir: ' + str(returnValue(dictionary, 'pir')))
   if (dictionary['button']):
      logging.info('button triggered')
      takePhoto()
   if (dictionary['pir']):
      logging.info('pir triggered')
      takePhoto()


def on_subscribe(client, userdata, mid, granted_qos):
   logging.info('Subscribed: ' +  str(userdata) + ' ' + str(mid) + ' ' + str(granted_qos))


def on_log(client, userdata, level, buf):
   logging.debug(buf)


def returnValue(dictionary, key):
   if (key in dictionary):
      return dictionary[key]
   else:
      return ''


def main():
   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_log = on_log
   client.username_pw_set(username=USERNAME, password=PASSWORD)
   client.connect(BROKER_ADDRESS)
   for node in NODES:
      client.subscribe(node + TOPIC)
   client.loop_forever()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      if (checkLockFile()):
         os.remove(LOCK_FILE)
      sys.exit('interrupted')
      pass

