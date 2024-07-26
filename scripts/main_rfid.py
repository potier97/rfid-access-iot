import ubinascii
from machine import unique_id
from rfid import Rfid

if __name__ == '__main__':
  client_id = ubinascii.hexlify(unique_id())
  # Cambiarlo por la ip del broker
  mqtt_server = '192.168.1.24'
  # Cambiarlo por el nombre del dispositivo desplegado
  thing_name = 'thing'
  rfid_controller = Rfid(mqtt_server, client_id, thing_name)
  rfid_controller.listen()