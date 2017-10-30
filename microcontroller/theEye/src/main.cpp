#include <Arduino.h>


// defines
#ifndef VERSION
#define VERSION "theEye"
#endif
#ifndef SERVER
#define SERVER  "lemonpi"
#endif
#ifndef PORT
#define PORT    80
#endif
#ifndef PATH
#define PATH    "/esp/update/arduino.php"
#endif


// libraries
#include <Streaming.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <WiFiManager.h>
#include <ArduinoJson.h>
#include <FS.h>
#include <ESP8266httpUpdate.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>


// constants
const char file[]="/config.json";


// switch adc port to monitor vcc
ADC_MODE(ADC_VCC);


// global definitions
PubSubClient pubSubClient;
WiFiClient wifiClient;


// global variables
bool shouldSaveConfig = false;
char id[13];
char mqtt_server[40] = "test.mosquitto.org";
char mqtt_username[16] = "";
char mqtt_password[16] = "";
char mqtt_port[6] = "1883";
String publishTopic = "/value";
int pirPin = D1;
int buttonPin = D2;
bool pirDetected = false;
bool buttonDetected = false;


// callback functions
void saveConfigCallback ();


// functions
void setupHardware();
void printSettings();
void setupWiFiManager(bool);
void readConfig();
void saveConfig();
void updater();
void setupID();
void setupPubSub();
void setupTopic();
bool connect();
void setupOTA();
void publishValues();
unsigned int getVcc();


void setup() {
  setupHardware();
  printSettings();
  setupWiFiManager(true);
  updater();
  setupID();
  setupPubSub();
  setupTopic();
  connect();
  setupOTA();
}

void loop() {
  ArduinoOTA.handle();

  if (WiFi.status() == WL_CONNECTED) {
    if (!pubSubClient.connected()) {
      connect();
    } else {
      pubSubClient.loop();
      if ((digitalRead(buttonPin) == LOW) and (!buttonDetected)) {
        digitalWrite(BUILTIN_LED, LOW);
        buttonDetected = true;
        publishValues();
      }
      if ((digitalRead(buttonPin) == HIGH) and (buttonDetected)) {
        digitalWrite(BUILTIN_LED, HIGH);
        buttonDetected = true;
      }
      if ((digitalRead(pirPin) == HIGH) and (!pirDetected)) {
        digitalWrite(BUILTIN_LED, LOW);
        pirDetected = true;
        publishValues();
      }
      if ((digitalRead(pirPin) == LOW) and (pirDetected)) {
        digitalWrite(BUILTIN_LED, HIGH);
        pirDetected = false;
      }
    }
  }
}


void saveConfigCallback () {
  shouldSaveConfig = true;
  Serial << "Should save config" << endl;
}

void setupHardware() {
  Serial.begin(115200);
  pinMode(BUILTIN_LED, OUTPUT);
  pinMode(pirPin, INPUT_PULLUP);
  pinMode(buttonPin, INPUT_PULLUP);
}

void printSettings() {
  Serial << endl << endl << "RESETINFO: " << ESP.getResetInfo() << endl;
  Serial << endl << "VERSION: " << VERSION << endl;
  Serial << "SERVER: " << SERVER << endl;
  Serial << "PORT: " << PORT << endl;
  Serial << "PATH: " << PATH << endl;
  Serial << endl;
}

void setupWiFiManager(bool autoConnect) {
  readConfig();
  WiFiManagerParameter custom_mqtt_server("server", "mqtt server", mqtt_server, 40);
  WiFiManagerParameter custom_mqtt_port("port", "mqtt port", mqtt_port, 6);
  WiFiManagerParameter custom_mqtt_username("username", "mqtt username", mqtt_username, 16);
  WiFiManagerParameter custom_mqtt_password("password", "mqtt password", mqtt_password, 16);
  WiFiManager wifiManager;
  #ifdef VERBOSE
  wifiManager.setDebugOutput(true);
  #else
  wifiManager.setDebugOutput(false);
  #endif
  wifiManager.setSaveConfigCallback(saveConfigCallback);
  wifiManager.addParameter(&custom_mqtt_server);
  wifiManager.addParameter(&custom_mqtt_port);
  wifiManager.addParameter(&custom_mqtt_username);
  wifiManager.addParameter(&custom_mqtt_password);
  if (autoConnect) {
    wifiManager.setTimeout(180);
    if (!wifiManager.autoConnect("AutoConnectAP")) {
      Serial << "failed to connect and hit timeout" << endl;
    } else {
      Serial << "WiFi connected" << endl;
      strcpy(mqtt_server, custom_mqtt_server.getValue());
      strcpy(mqtt_port, custom_mqtt_port.getValue());
      strcpy(mqtt_username, custom_mqtt_username.getValue());
      strcpy(mqtt_password, custom_mqtt_password.getValue());
      if (shouldSaveConfig) {
        saveConfig();
      }
      Serial << "local ip: " << WiFi.localIP() << endl;
    }
  } else {
    wifiManager.setTimeout(180);
    if (!wifiManager.startConfigPortal("OnDemandAP")) {
      Serial << "failed to connect and hit timeout" << endl;
    } else {
      Serial << "WiFi connected" << endl;
      strcpy(mqtt_server, custom_mqtt_server.getValue());
      strcpy(mqtt_port, custom_mqtt_port.getValue());
      strcpy(mqtt_username, custom_mqtt_username.getValue());
      strcpy(mqtt_password, custom_mqtt_password.getValue());
      if (shouldSaveConfig) {
        saveConfig();
      }
      Serial << "local ip: " << WiFi.localIP() << endl;
    }
  }
}

void readConfig() {
  Serial << "mounting FS..." << endl;
  if (SPIFFS.begin()) {
    Serial << "mounted file system" << endl;
    if (SPIFFS.exists(file)) {
      Serial << "reading config file" << endl;
      File configFile = SPIFFS.open(file, "r");
      if (configFile) {
        Serial << "opened config file" << endl;;
        size_t size = configFile.size();
        std::unique_ptr<char[]> buf(new char[size]);
        configFile.readBytes(buf.get(), size);
        DynamicJsonBuffer jsonBuffer;
        JsonObject& json = jsonBuffer.parseObject(buf.get());
        #ifdef VERBOSE
        json.prettyPrintTo(Serial);
        Serial << endl;
        #endif
        if (json.success()) {
          Serial << "parsed json" << endl;
          if (json.containsKey("mqtt_server") && json.containsKey("mqtt_port") && json.containsKey("mqtt_username") && json.containsKey("mqtt_password")) {
            strcpy(mqtt_server, json["mqtt_server"]);
            strcpy(mqtt_port, json["mqtt_port"]);
            strcpy(mqtt_username, json["mqtt_username"]);
            strcpy(mqtt_password, json["mqtt_password"]);
          }
        } else {
          Serial << "failed to load json config" << endl;
        }
      }
    }
  } else {
    Serial << "failed to mount FS" << endl;
  }
}

void saveConfig() {
  Serial << "saving config" << endl;
  DynamicJsonBuffer jsonBuffer;
  JsonObject& json = jsonBuffer.createObject();
  File configFile = SPIFFS.open(file, "w");

  if (configFile) {
    json["mqtt_server"] = mqtt_server;
    json["mqtt_port"] = mqtt_port;
    json["mqtt_username"] = mqtt_username;
    json["mqtt_password"] = mqtt_password;
    #ifdef VERBOSE
    json.prettyPrintTo(Serial);
    Serial << endl;
    #endif
    json.printTo(configFile);
    configFile.close();
  } else {
    Serial << "failed to open config file for writing" << endl;
  }
}

void updater() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial << "try update" << endl;
    t_httpUpdate_return ret = ESPhttpUpdate.update(SERVER, PORT, PATH, VERSION);
    switch (ret) {
      case HTTP_UPDATE_FAILED:
      Serial << "HTTP_UPDATE_FAILD Error (" << ESPhttpUpdate.getLastError() << "): " << ESPhttpUpdate.getLastErrorString().c_str() << endl;
      break;
      case HTTP_UPDATE_NO_UPDATES:
      Serial << "HTTP_UPDATE_NO_UPDATES" << endl;
      break;
      case HTTP_UPDATE_OK:
      Serial << "HTTP_UPDATE_OK" << endl;
      break;
    }
  }
}

void setupID() {
  byte mac[6];

  WiFi.macAddress(mac);
  sprintf(id, "%02x%02x%02x%02x%02x%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  Serial << "id: " << id << endl;
}

void setupPubSub() {
  pubSubClient.setClient(wifiClient);
  pubSubClient.setServer(mqtt_server, String(mqtt_port).toInt());
}

void setupTopic() {
  publishTopic = id + publishTopic;
}

bool connect() {
  bool connected = false;

  Serial << "Attempting MQTT connection (~5s) ..." << endl;
  if ((String(mqtt_username).length() == 0) || (String(mqtt_password).length() == 0)) {
    Serial << "trying without MQTT authentication" << endl;
    connected = pubSubClient.connect(id);
  } else {
    Serial << "trying with MQTT authentication" << endl;
    connected = pubSubClient.connect(id, String(mqtt_username).c_str(), String(mqtt_password).c_str());
  }
  if (connected) {
    Serial << "MQTT connected, rc=" << pubSubClient.state() << endl;
  } else {
    Serial << "MQTT failed, rc=" << pubSubClient.state() << endl;
  }

  return pubSubClient.connected();
}

void setupOTA() {
  ArduinoOTA.onStart([]() {
    Serial << "Start" << endl;
  });
  ArduinoOTA.onEnd([]() {
    Serial << "End" << endl;
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial << "Progress: " << (progress / (total / 100)) << "%" << endl;
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial << "Error[" << error << "]: ";
    if (error == OTA_AUTH_ERROR) Serial << "Auth Failed" << endl;
    else if (error == OTA_BEGIN_ERROR) Serial << "Begin Failed" << endl;
    else if (error == OTA_CONNECT_ERROR) Serial << "Connect Failed" << endl;
    else if (error == OTA_RECEIVE_ERROR) Serial << "Receive Failed" << endl;
    else if (error == OTA_END_ERROR) Serial << "End Failed" << endl;
  });
  ArduinoOTA.begin();
}

void publishValues() {
  DynamicJsonBuffer jsonBuffer;
  JsonObject& json = jsonBuffer.createObject();
  String jsonString;

  json.set("vcc", getVcc());
  json.set("button", buttonDetected);
  json.set("pir", pirDetected);
  if (pubSubClient.connected()) {
    jsonString = "";
    json.printTo(jsonString);
    if (pubSubClient.publish(publishTopic.c_str(), jsonString.c_str())) {
      Serial << " < " << publishTopic << ": " << jsonString << endl;
    } else {
      Serial << "!< " << publishTopic << ": " << jsonString << endl;
    }
  }
}

unsigned int getVcc() {
  return ESP.getVcc();
}
