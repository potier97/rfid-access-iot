import ubinascii
from machine import unique_id
from rfid import Rfid
import config

if __name__ == '__main__':
  mqtt_server = config.mqtt_server
  thing_name = config.thing_name
  thing_key = config.thing_key
  rfid_controller = Rfid(mqtt_server, thing_name, thing_key)
  rfid_controller.listen()