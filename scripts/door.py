import ujson
import os
from time import sleep
from machine import Pin, reset
from servo import Servo
import ubinascii
from umqtt.simple import MQTTClient

class Door:
  """
  Clase que representa una puerta controlada por un dispositivo IoT.

  Args:
    mqtt_server (str): Dirección del servidor MQTT.
    thing_name (str): Nombre del dispositivo IoT e ID del cliente MQTT.
    servo_pin (int, optional): Número de pin del servo. Por defecto es 14.
    led_pin (int, optional): Número de pin del LED. Por defecto es 16.
  """
  def __init__(self, 
    mqtt_server,
    thing_name,
    thing_key,
    ssl=True,
    servo_pin=14,
    led_pin=16):
    """
    Inicializa una instancia de la clase Door.

    Args:
      mqtt_server (str): Dirección del servidor MQTT.
      thing_name (str): Nombre del dispositivo IoT e ID del cliente MQTT.
      ssl (bool, optional): Indica si se debe usar SSL. Por defecto es True.
      servo_pin (int, optional): Número de pin del servo. Por defecto es 14.
      led_pin (int, optional): Número de pin del LED. Por defecto es 16.
    """
    self.mqtt_server = mqtt_server
    self.thing_name = f"{thing_name}_door"
    self.thing_key = thing_key
    self.ssl = ssl
    self.servo = Servo(pin=servo_pin)
    self.led = Pin(led_pin, Pin.OUT)
    self.locked = False
    self.state = {
      "state": {
        "reported": {
          "status": 'unlock',
          "led": 1
        }
      }
    }
    self.topics = {
      "open": f"{self.thing_name}/door/open".encode(),
      "close": f"{self.thing_name}/door/close".encode(),
      "lock": f"{self.thing_name}/door/lock".encode(),
      "unlock": f"{self.thing_name}/door/unlock".encode(),
      # ! Posible bug en el nombre del tema cuando se codifica por el $
      "shadow": "$aws/things/"+self.thing_name+"/shadow/update/delta"
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
    try:
      message = ujson.loads(msg)
    except:
      print('Mensaje no válido')
      return

    print('Contenido:', message)
    if not self.validate_key(message["key"]):
      print('Clave incorrecta')
      return

    if topic == self.topics["open"]:
      self.handle_open()
    elif topic == self.topics["close"]:
      self.handle_close()
    elif topic == self.topics["lock"]:
      self.handle_lock()
    elif topic == self.topics["unlock"]:
      self.handle_unlock()
    elif topic == self.topics["shadow"]:
      self.handle_shadow(msg)


  def validate_key(self, key):
    """
    Valida la clave del dispositivo.

    Args:
      key (str): Clave del dispositivo.

    Returns:
      bool: True si la clave es válida, False en caso contrario.
    """
    return key == self.thing_key

  def handle_open(self):
    """
    Maneja la acción de abrir la puerta.
    """
    if not self.locked and self.servoPos == 0:
      print('ESP recibió el mensaje de abrir la puerta')
      self.servoPos = 180
      self.servo.move(180)
      self.state["state"]["reported"]["status"] = 'open'

  def handle_close(self):
    """
    Maneja la acción de cerrar la puerta.
    """
    if not self.locked and self.servoPos == 180:
      print('ESP recibió el mensaje de cerrar la puerta')
      self.servoPos = 0
      self.servo.move(0)
      self.state["state"]["reported"]["status"] = 'close'

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
    self.state["state"]["reported"]["status"] = 'lock'

  def handle_unlock(self):
    """
    Maneja la acción de desbloquear la puerta.
    """
    print('ESP recibió el mensaje de desbloquear la puerta')
    self.locked = False
    self.led.value(1)
    self.state["state"]["reported"]["status"] = 'unlock'

  def handle_shadow(self, msg):
    """
    Maneja el mensaje de sombra recibido.

    Args:
      msg (bytes): Contenido del mensaje de sombra.
    """
    message = ujson.loads(msg)
    print('Mensaje de sombra:', message)
    if message['state']['desired']['status'] == 'open':
      self.handle_open()
    elif message['state']['desired']['status'] == 'close':
      self.handle_close()
    elif message['state']['desired']['status'] == 'lock':
      self.handle_lock()
    elif message['state']['desired']['status'] == 'unlock':
      self.handle_unlock()
    
    #CAMBIO DE ESTADO DE LED
    if message['state']['desired']['led']:
      self.led.value(message['state']['desired']['led'])

  def restart_and_reconnect(self):
    """
    Reinicia y reconecta al broker MQTT en caso de error de conexión.
    """
    print('Error al conectar al broker MQTT. Reconectando...')
    sleep(5)
    reset()

  def read_cert(self, filename):        
    """
    Lee un archivo de certificado y lo decodifica.
    Args:
      filename (str): Nombre del archivo de certificado.
    Returns:
      bytes: Contenido del archivo decodificado.
    """
    with open(filename, 'r') as f:
      text = f.read().strip()
      split_text = text.split('\n')
      base64_text = ''.join(split_text[1:-1])
      return ubinascii.a2b_base64(base64_text)

  def connect_and_subscribe(self):
    """
    Conecta al servidor MQTT y se suscribe a los temas necesarios.

    Returns:
      MQTTClient: Cliente MQTT conectado y suscrito.
    """
    private_key = "private.pem.key"
    private_cert = "cert.pem.crt"
    key = self.read_cert(private_key)
    cert = self.read_cert(private_cert)
    sslp = {
      'key': key,
      'cert': cert,
      'server_side': False
    }
    print('Conectando al broker MQTT...')
    client = MQTTClient(client_id=self.thing_name, server=self.mqtt_server, port=8883, keepalive=1200, ssl=True, ssl_params=sslp) if self.ssl else MQTTClient(self.thing_name, self.mqtt_server, keepalive=60)
    try:
      client.set_callback(self.sub_cb)
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
    