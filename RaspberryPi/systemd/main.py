#!/usr/bin/env python

#mosquitto_pub -h theeye -t 5ccf7f3c8da1/value -u esp8266 -P 0acht15 -m "{\"vcc\":3032,\"button\":false,\"pir\":true}"

import paho.mqtt.client as mqtt
import json
import logging
import time
import os


logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


BROKER_ADDRESS = 'theEye'
USERNAME = 'esp8266'
PASSWORD = '0acht15'
NODE = '5ccf7f3c8da1'
TOPIC = '/value'
LOCK_FILE = '/run/takePhoto.lock'
GALLERY = '/var/www/html/gallery/'


def createLockFile():
   f = open(LOCK_FILE, "w+")


def checkLockFile():
   return os.path.isfile(LOCK_FILE)


def takePhoto(path):
   if (not checkLockFile()):
      logging.warning("takePhoto")
      createLockFile()
      timestr = time.strftime("%Y%m%d-%H%M%S")
      cmd = "raspistill -t 1 -o {0}{1}.jpg 2>&1".format(path, timestr)
      os.system(cmd)
      os.remove(LOCK_FILE)
   else:
      logging.warning("takePhoto blocked")


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
      takePhoto(GALLERY)
   if (dictionary['pir']):
      takePhoto("/tmp/")


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
   client.subscribe(NODE + TOPIC)
   client.loop_forever()


if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      sys.exit('interrupted')
      pass

