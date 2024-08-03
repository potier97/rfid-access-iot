import ubinascii
from machine import unique_id
from rfid import Rfid
import config

if __name__ == '__main__':
  client_id = ubinascii.hexlify(unique_id())
  mqtt_server = config.mqtt_server
  thing_name = config.thing_name
  rfid_controller = Rfid(mqtt_server, client_id, thing_name)
  rfid_controller.listen()