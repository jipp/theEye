#!/usr/bin/env python

# mosquitto_pub -h theEye -t cam/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":false,\"pir\":true}"
# mosquitto_pub -h theEye -t cam1/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":true,\"pir\":false}"


import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import logging
import time
import os
import sys
import ConfigParser
import paramiko
import picamera
import platform


#logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
logging.getLogger("paramiko.transport").setLevel(logging.INFO)
#paramiko.util.log_to_file('/tmp/paramiko.log')


camera = picamera.PiCamera()
config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')


LOCAL_GALLERY_FOLDER = config.get('local', 'gallery_folder')
LOCAL_LOCATION = config.get('local', 'location')
MQTT_BROKER_ADDRESS = config.get('mqtt', 'broker_address')
MQTT_USERNAME = config.get('mqtt', 'username')
MQTT_PASSWORD = config.get('mqtt', 'password')
MQTT_NODES = config.get('mqtt', 'nodes').split(',')
CAMERA_ID = platform.node()
CAMERA_EXTENSION = config.get('camera', 'extension')
camera.rotation = config.get('camera', 'rotation')
camera.hflip = config.getboolean('camera', 'hflip')
camera.vflip = config.getboolean('camera', 'vflip')
camera.resolution = (config.getint('camera', 'width'), config.getint('camera', 'height'))
camera.led = config.getboolean('camera', 'led')
REMOTE_HOST = config.get('remote', 'host')
REMOTE_ENABLED = config.getboolean('remote', 'enabled')
REMOTE_USERNAME = config.get('remote', 'username')
REMOTE_PASSWORD = config.get('remote', 'password')
REMOTE_FOLDER = config.get('remote', 'remote_folder')



def takePhoto():
   timestr = time.strftime("%Y%m%d-%H%M%S")
   file = "{0}-{1}.{2}".format(CAMERA_ID, timestr, CAMERA_EXTENSION)
   picture = "{0}/{1}".format(LOCAL_GALLERY_FOLDER, file)
   logging.warning('saving picture: ' + picture)
   camera.capture(picture)
   if (REMOTE_ENABLED):
      upload(LOCAL_GALLERY_FOLDER, file)
   return picture


def upload(folder, file):
   localfile = "{0}/{1}".format(folder, file)
   remotefile = "{0}/{1}".format(REMOTE_FOLDER, file)
   transport = paramiko.Transport((REMOTE_HOST, 22))
   transport.connect(username = REMOTE_USERNAME, password = REMOTE_PASSWORD)
   sftp = paramiko.SFTPClient.from_transport(transport)
   try:
      sftp.put(localfile, remotefile)
   except Exception as e:
      print(e)
      print('host: ' + REMOTE_HOST + '; username: ' + REMOTE_USERNAME + '; password: ' + REMOTE_PASSWORD)
      print(localfile + ' -> ' + remotefile)
   sftp.close()
   transport.close()


def on_connect(client, userdata, flags, rc):
   logging.info('rc: ' + str(rc))


def on_disconnect(client, userdata, rc):
   logging.info('rc: ' + str(rc))


def on_message(client, userdata, message):
   logging.info('topic: ' + message.topic + ', qos:  ' + str(message.qos) + ', payload:  ' + str(message.payload))
   try:
      payload = json.loads(message.payload)
      node = message.topic.split("/")[0]
      for key in payload:
         if key != 'vcc':
            if payload[key]:
               logging.info(key + ' triggered')
               picture = takePhoto()
               publish.single(CAMERA_ID + "/status", "{\"location\":" + LOCAL_LOCATION + ",\"node\":" + node + ",\"picture\":" + picture + "}", hostname = MQTT_BROKER_ADDRESS, auth = {'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})
   except Exception as e:
      print(e)


def on_subscribe(client, userdata, mid, granted_qos):
   logging.info('mid: ' + str(mid) + ', granted_qos: ' + str(granted_qos))


def on_log(client, userdata, level, buf):
   logging.debug(buf)


def main():
   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_disconnect = on_disconnect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_log = on_log
   client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
   client.connect(MQTT_BROKER_ADDRESS)
   client.subscribe(CAMERA_ID + "/value")
   if not MQTT_NODES:
      for node in MQTT_NODES:
         client.subscribe(node + "/value")
   client.loop_forever()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      sys.exit('interrupted')
