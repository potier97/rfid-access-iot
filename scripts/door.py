from time import sleep
from machine import Pin, reset
from umqtt.simple import MQTTClient
from servo import Servo
import ubinascii

class Door:
  """
  Clase que representa una puerta controlada por un dispositivo IoT.

  Args:
    mqtt_server (str): Dirección del servidor MQTT.
    client_id (str): ID del cliente MQTT.
    thing_name (str): Nombre del dispositivo IoT.
    servo_pin (int, optional): Número de pin del servo. Por defecto es 14.
    led_pin (int, optional): Número de pin del LED. Por defecto es 16.
  """

  def __init__(self, mqtt_server, client_id, thing_name, servo_pin=14, led_pin=16):
    """
    Inicializa una instancia de la clase Door.

    Args:
      mqtt_server (str): Dirección del servidor MQTT.
      client_id (str): ID del cliente MQTT.
      thing_name (str): Nombre del dispositivo IoT.
      servo_pin (int, optional): Número de pin del servo. Por defecto es 14.
      led_pin (int, optional): Número de pin del LED. Por defecto es 16.
    """
    self.mqtt_server = mqtt_server
    self.client_id = client_id
    self.thing_name = thing_name
    self.servo = Servo(pin=servo_pin)
    self.led = Pin(led_pin, Pin.OUT)
    self.locked = False
    self.topics = {
      "open": f"{thing_name}/door/open".encode(),
      "close": f"{thing_name}/door/close".encode(),
      "lock": f"{thing_name}/door/lock".encode(),
      "unlock": f"{thing_name}/door/unlock".encode()
    }
    self.client = self.connect_and_subscribe()
    self.servo.move(0)
    self.led.value(1)
    self.servoPos = 0

  def sub_cb(self, topic, msg):
    """
    Callback para manejar los mensajes MQTT recibidos.

    Args:
      topic (bytes): El tema del mensaje MQTT.
      msg (bytes): El contenido del mensaje MQTT.
    """
    print((topic, msg))
    if topic == self.topics["open"]:
      self.handle_open()
    elif topic == self.topics["close"]:
      self.handle_close()
    elif topic == self.topics["lock"]:
      self.handle_lock()
    elif topic == self.topics["unlock"]:
      self.handle_unlock()

  def handle_open(self):
    """
    Maneja la acción de abrir la puerta.
    """
    if not self.locked and self.servoPos == 0:
      print('ESP recibió el mensaje de abrir la puerta')
      self.servoPos = 180
      self.servo.move(180)

  def handle_close(self):
    """
    Maneja la acción de cerrar la puerta.
    """
    if not self.locked and self.servoPos == 180:
      print('ESP recibió el mensaje de cerrar la puerta')
      self.servoPos = 0
      self.servo.move(0)

  def handle_lock(self):
    """
    Maneja la acción de bloquear la puerta.
    """
    print('ESP recibió el mensaje de bloquear la puerta')
    self.locked = True
    if self.servoPos == 180:
      self.servoPos = 0
      self.servo.move(0)
    self.led.value(0)

  def handle_unlock(self):
    """
    Maneja la acción de desbloquear la puerta.
    """
    print('ESP recibió el mensaje de desbloquear la puerta')
    self.locked = False
    self.led.value(1)

  def restart_and_reconnect(self):
    """
    Reinicia y reconecta al broker MQTT en caso de error de conexión.
    """
    print('Error al conectar al broker MQTT. Reconectando...')
    sleep(5)
    reset()

  def connect_and_subscribe(self):
    """
    Conecta al servidor MQTT y se suscribe a los temas necesarios.

    Returns:
      MQTTClient: Cliente MQTT conectado y suscrito.
    """
    client = MQTTClient(self.client_id, self.mqtt_server, keepalive=60)
    client.set_callback(self.sub_cb)
    try:
      client.connect()
      print(f'Conectado al broker MQTT {self.mqtt_server}')
      for topic in self.topics.values():
        client.subscribe(topic)
        print(f'Suscrito al tema {topic}')
      return client
    except OSError as e:
      print(f'Error de conexión: {e}')
      self.restart_and_reconnect()

  def listen(self):
    """
    Escucha los mensajes MQTT y maneja las excepciones.
    """
    try:
      while True:
        self.client.wait_msg()
    except OSError as e:
      print(f'OSError: {e}')
      self.restart_and_reconnect()
    except Exception as e:
      print(f'Excepción: {e}')
      self.restart_and_reconnect()
    finally:
      print("Limpiando")
      self.client.disconnect()
    