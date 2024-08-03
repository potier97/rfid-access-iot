from machine import Pin, SoftSPI, reset
from time import sleep
from umqtt.simple import MQTTClient
import ubinascii
import mfrc522
import ujson
import os

class Rfid:
  def __init__(self,
    mqtt_server,
    thing_name,
    thing_group,
    thing_key,
    ssl=True,
    led_pin=16,
    sck_pin=14,
    mosi_pin=13,
    miso_pin=12):
    """
    Inicializa una instancia de la clase Rfid.

    Args:
      mqtt_server (str): Dirección del servidor MQTT.
      thing_name (str): Nombre del dispositivo IoT.
      led (int, optional): Número de pin del LED. Por defecto es 16.
      sck (int, optional): Número de pin del reloj SPI. Por defecto es 14.
      mosi (int, optional): Número de pin de datos de salida SPI. Por defecto es 13.
      miso (int, optional): Número de pin de datos de entrada SPI. Por defecto es 12.
    """
    # Inicializa el LED
    self.led = Pin(led_pin, Pin.OUT)
    self.ssl = ssl
    # Key del dispositivo
    self.thing_key = thing_key
    # Configuración del lector RFID
    self.sck = Pin(sck_pin, Pin.OUT)
    self.mosi = Pin(mosi_pin, Pin.OUT)
    self.miso = Pin(miso_pin, Pin.IN)
    # Estado de la rfid
    self.state = "locked"  # Otros estados: "ready", "remove", "update"
    self.state = {
      "state": {
        "reported": {
          "status": 'locked',
          "led": 1
        }
      }
    }
    # Configuración del cliente MQTT
    self.mqtt_server = mqtt_server
    self.thing_group = f"{thing_group}_group"
    self.thing_name = f"{thing_name}_rfid"
    # Configuración con lector RFID
    self.spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
    self.spi.init()
    self.rdr = mfrc522.MFRC522(self.spi, gpioRst=4, gpioCs=5)
    # Configuración de los temas MQTT - Suscripcion
    self.topics = {
      "status": f"{self.thing_name}/{self.thing_group}/rfid/status".encode(),
      # ! Posible bug en el nombre del tema cuando se codifica por el $
      "shadow": "$aws/things/"+self.thing_name+"/shadow/update/delta"
    }
    # Publicaciones
    self.publish = {
      "open": f"{self.thing_name}/{self.thing_group}/rfid/open".encode(),
      "remove": f"{self.thing_name}/{self.thing_group}/rfid/remove".encode(),
      "update": f"{self.thing_name}/{self.thing_group}/rfid/update".encode(),
    }
    self.client = self.connect_and_subscribe()

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

    if topic == self.topics["status"]:
      self.handle_status(message["state"])
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

  def handle_status(self, state):
    """
    Maneja el cambio de estado del dispositivo.

    Args:
      state (str): Nuevo estado del dispositivo.
    """
    if state in ["locked", "ready", "remove", "update"]:
        print(f'Cambio de estado a {state}')
        self.state = state
        self.update_led()

  def handle_shadow(self, msg):
    """
    Maneja el mensaje de sombra recibido.

    Args:
      msg (bytes): Contenido del mensaje de sombra.
    """
    message = ujson.loads(msg)
    print('Mensaje de sombra:', message)
    if message['state']['reported']['status']:
      self.state['state']['reported']['status'] = message['state']['reported']['status']

    if message['state']['reported']['led']:
      self.state['state']['reported']['led'] = message['state']['reported']['led']


  def update_led(self):
    """
    Actualiza el estado del LED según el estado del dispositivo.
    """
    if self.state == "locked":
        self.led_blink(3, 0.25)
    elif self.state == "ready":
        self.led.value(1)
    elif self.state == "remove":
        self.led_blink(7, 0.25)
    elif self.state == "update":
        self.led_blink(5, 0.25)


  def led_blink(self, times, interval):
    """
    Parpadea el LED un número de veces con un intervalo específico.
    
    Args:
      times (int): Número de parpadeos.
      interval (float): Intervalo entre parpadeos.
    """
    for _ in range(times):
      self.led.value(1)
      sleep(interval)
      self.led.value(0)
      sleep(interval)
    self.led.value(0)

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


  def check_rfid(self):
    """
    Verifica las tarjetas RFID y maneja las operaciones según el estado.
    """
    try:
      (stat, tag_type) = self.rdr.request(self.rdr.REQIDL)
      if stat == self.rdr.OK:
        (stat, uid) = self.rdr.anticoll()
        if stat == self.rdr.OK:
          uid_hex = ''.join(['{:02X}'.format(x) for x in uid])
          message = ujson.dumps({
              "thing": self.thing_name,
              "group": self.thing_group,
              "type": "0x%02x" % tag_type,
              "uid": uid_hex,
              "key": self.thing_key
          })
          # print(f'Tarjeta detectada: {message}')
          if self.state == "ready":
            print(f'Verificando tarjeta {uid_hex}')
            self.client.publish(self.publish["open"], message)
          elif self.state == "remove":
            print(f'Eliminando Tarjeta {uid_hex}')
            self.client.publish(self.publish["remove"], message)
          elif self.state == "update":
            print(f'Añadiendo Tarjeta {uid_hex}')
            self.client.publish(self.publish["update"], message)
          self.led_blink(3, 0.5)
          self.led.value(1)
    except Exception as e:
      print(f'Error al leer tarjeta: {e}')
      self.restart_and_reconnect()

  def listen(self):
    """
    Escucha los mensajes MQTT y maneja las excepciones.
    """
    try:
      while True:
        self.client.check_msg()
        self.check_rfid()
    except OSError as e:
      print(f'OSError: {e}')
      self.restart_and_reconnect()
    except Exception as e:
      print(f'Excepción: {e}')
      self.restart_and_reconnect()
    finally:
      print("Limpiando")
      self.client.disconnect()

