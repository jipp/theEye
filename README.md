# theEye
trigger any action from anywhere without changing existing infrastructure - wifi, 4g, 5g is evolving and replacing specialized infrastructures:
* in case of an accident status photo can be recorded by local and/or remote trigger
  * car accident, theft
  * elevator emergency
* use of an secured communication

elements:
* actor - raspberry
  * using camera
* broker - raspberry
  * mqtt - mosquitto
* publisher - raspberry
  * webserver - lightthpd
  * gallery - Single File PHP Gallery
* sensor with wifi connectivity - esp8266
  * switch
  * PIR

benefits:
* no Firewall changes needed to enable communication
* several sensors can trigger the same action
* scalable

next steps:
* integration to APPIoT 
