import ubinascii
from machine import unique_id
from door import Door

if __name__ == '__main__':
  client_id = ubinascii.hexlify(unique_id())
  # Cambiarlo por la ip del broker
  mqtt_server = '192.168.1.24'
  # Cambiarlo por el nombre del dispositivo desplegado
  thing_name = 'thing'
  door_controller = Door(mqtt_server, client_id, thing_name)
  door_controller.listen()