import os
import time
from door import Door
import config

if __name__ == '__main__':
  mqtt_server = config.mqtt_server
  thing_name = config.thing_name
  thing_key = config.thing_key
  door_controller = Door(mqtt_server, thing_name, thing_key)
  door_controller.listen()