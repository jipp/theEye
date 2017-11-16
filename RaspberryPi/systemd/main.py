#!/usr/bin/env python

# apt -y install python-pip
# apt -y install python-paramiko
# pip install paho-mqtt
# apt apt -y install lighttpd

#mosquitto_pub -h theEye -t test/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":false,\"pir\":true}"
#mosquitto_pub -h theEye -t test/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":true,\"pir\":false}"


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
#paramiko.util.log_to_file('/tmp/paramiko.log')


config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')


PATH_LOCK_FILE = config.get('path', 'lock_file')
PATH_GALLERY = config.get('path', 'gallery')
MQTT_BROKER_ADDRESS = config.get('mqtt', 'broker_address')
MQTT_USERNAME = config.get('mqtt', 'username')
MQTT_PASSWORD = config.get('mqtt', 'password')
MQTT_NODES = config.get('mqtt', 'nodes').split(',')
MQTT_TOPIC = config.get('mqtt', 'topic')
CAMERA_COMMAND = config.get('camera', 'command')
CAMERA_PARAMETER = config.get('camera', 'parameter')
CAMERA_ID = config.get('camera', 'id')
CAMERA_EXTENSION = config.get('camera', 'extension')
REMOTE_HOST = config.get('remote', 'host')
REMOTE_ENABLED = config.getboolean('remote', 'enabled')
REMOTE_USERNAME = config.get('remote', 'username')
REMOTE_PASSWORD = config.get('remote', 'password')
REMOTE_FOLDER = config.get('remote', 'remoteFolder')

def createLockFile():
   f = open(PATH_LOCK_FILE, "w+")


def checkLockFile():
   return os.path.isfile(PATH_LOCK_FILE)


def takePhoto():
   if (not checkLockFile()):
      createLockFile()
      timestr = time.strftime("%Y%m%d-%H%M%S")
      file = "{0}-{1}.{2}".format(CAMERA_ID, timestr, CAMERA_EXTENSION)
      cmd = "{0} {1} {2}{3} 2>&1".format(CAMERA_COMMAND, CAMERA_PARAMETER, PATH_GALLERY, file)
      logging.warning(cmd)
      os.system(cmd)
      os.remove(PATH_LOCK_FILE)
      if (REMOTE_ENABLED):
         upload(PATH_GALLERY, file)
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
   client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
   client.connect(MQTT_BROKER_ADDRESS)
   for node in MQTT_NODES:
      client.subscribe(node + MQTT_TOPIC)
   client.loop_forever()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      if (checkLockFile()):
         os.remove(PATH_LOCK_FILE)
      sys.exit('interrupted')
      pass
