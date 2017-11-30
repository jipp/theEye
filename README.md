# theEye

elements:
* actor - Raspberry
  * using camera
* sensor - can be using either wifi (esp8266) or cable
  * manual/script - trigger.py
  * switch
  * PIR
* broker - Raspberry
  * mqtt - mosquitto
* publisher - Raspberry
  * webserver - lightthpd
  * web gallery - Single File PHP Gallery (sfpg)

possible next steps:
* integration to APPIoT 
