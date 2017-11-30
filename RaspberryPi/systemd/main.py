#!/usr/bin/env python

# mosquitto_pub -h lemonpi -t theEye1/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"manual\":true}"
# mosquitto_sub -v -h lemonpi -t theEye1/# -u esp8266 -P 0acht15

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import logging
import time
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

try:
   camera = picamera.PiCamera()
except Exception as e:
   print(e)
   sys.exit('interrupted')


client = mqtt.Client()
config = ConfigParser.ConfigParser()
config.read('/data/theEye/RaspberryPi/theEye.ini')

local_folder = config.get('local', 'folder')
local_description = config.get('local', 'description')
mqtt_host = config.get('mqtt', 'host')
mqtt_username = config.get('mqtt', 'username')
mqtt_password = config.get('mqtt', 'password')
mqtt_nodes = config.get('mqtt', 'nodes').split(',')
mqtt_status = config.get('mqtt', 'status')
camera.rotation = config.get('camera', 'rotation')
camera.hflip = config.getboolean('camera', 'hflip')
camera.vflip = config.getboolean('camera', 'vflip')
camera.resolution = (config.getint('camera', 'width'), config.getint('camera', 'height'))
camera.led = config.getboolean('camera', 'led')
remote_enabled = config.getboolean('remote', 'enable')
remote_host = config.get('remote', 'host')
remote_username = config.get('remote', 'username')
remote_password = config.get('remote', 'password')
remote_folder = config.get('remote', 'folder')
id = platform.node()


def takePhoto(picture, sensor, trigger):
   output = "{0}/{1}".format(local_folder, picture)
   camera.capture(output)
   logging.info('saving output: ' + output)
   publish.single(mqtt_status + "/status", "{\"id\":" + id + ",\"description\":" + local_description + ",\"sensor\":" + sensor + ",\"trigger\":" + trigger + ",\"picture\":" + picture + ",\"upload\":" + str(remote_enabled) + "}", hostname = mqtt_host, auth = {'username': mqtt_username, 'password': mqtt_password})
   if (remote_enabled):
      upload(picture)


def upload(picture):
   localfile = "{0}/{1}".format(local_folder, picture)
   remotefile = "{0}/{1}".format(remote_folder, picture)
   transport = paramiko.Transport((remote_host, 22))
   transport.connect(username = remote_username, password = remote_password)
   sftp = paramiko.SFTPClient.from_transport(transport)
   try:
      sftp.put(localfile, remotefile)
   except Exception as e:
      print(e)
      print('host: ' + remote_host + '; username: ' + remote_username + '; password: ' + remote_password)
      print(localfile + ' -> ' + remotefile)
   sftp.close()
   transport.close()


def get_picture_name():
   timestr = time.strftime("%Y%m%d-%H%M%S")
   picture = "{0}-{1}.jpg".format(id, timestr)
   return picture


def on_connect(client, userdata, flags, rc):
   logging.info('on_connect rc: ' + str(rc))
   client.subscribe(id + "/value")
   for node in mqtt_nodes:
      client.subscribe(node + "/value")


def on_disconnect(client, userdata, rc):
   logging.info('on_disconnect rc: ' + str(rc))


def on_message(client, userdata, message):
   logging.info('topic: ' + message.topic + ', qos: ' + str(message.qos) + ', payload: ' + str(message.payload))
   try:
      payload = json.loads(message.payload)
      sensor = message.topic.split("/")[0]
      for key in payload:
         if key != 'vcc':
            if payload[key]:
               logging.info(key + ' triggered')
               picture = get_picture_name()
               takePhoto(picture, sensor, key)
   except Exception as e:
      print(e)


def on_subscribe(client, userdata, mid, granted_qos):
   logging.info('mid: ' + str(mid) + ', granted_qos: ' + str(granted_qos))


def on_log(client, userdata, level, buf):
   logging.debug(buf)


def main():
#   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_disconnect = on_disconnect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_log = on_log
   client.username_pw_set(username=mqtt_username, password=mqtt_password)
   client.connect(mqtt_host)
   client.loop_forever()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      camera.close()
      client.disconnect()
      sys.exit('interrupted')
