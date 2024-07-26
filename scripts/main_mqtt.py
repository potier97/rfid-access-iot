import machine
import time

led = machine.Pin(16, machine.Pin.OUT)
print("Hola, ESP8266!")

# while True:
#     led.value(not led.value())
#     time.sleep(0.1)

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification':
    print('ESP received hello message')
  elif topic == b'led-on':
    print('ESP received led-on message')
    led.value(1)
  elif topic == b'led-off':
    print('ESP received led-off message')
    led.value(0)

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  print("Connecting to %s" % mqtt_server)
  print("Client ID: %s" % client_id)
  print("Topic Sub: %s" % topic_sub)
  client = MQTTClient(client_id, mqtt_server, user="", password="")
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(1)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'Hello #%d' % counter
      client.publish(topic_pub, msg)
      last_message = time.time()
      counter += 1
  except OSError as e:
    print("OSError")
    print(e)
    restart_and_reconnect()