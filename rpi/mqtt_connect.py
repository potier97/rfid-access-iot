import paho.mqtt.client as mqtt
import ssl
import json
import time

# certificados descargados
ca_path = "AmazonRootCA1.pem"
cert_path = "certificate.pem.crt"
key_path = "private.pem.key"

# Configuración de la conexión
mqtt_endpoint = "<endpoint>.iot.<region>.amazonaws.com"
# ID del cliente MQTT (debe ser único y con este se configura las politicas)
client_id = "MyRaspberryPi"

# Temas de los que se publicarán mensajes para actualizar el shadow -debe usar el nombre del client_id
shadow_update_topic = "$aws/things/MyRaspberryPi/shadow/update"
# Tema del que se recibirán actualizaciones del shadow
shadow_delta_topic = "$aws/things/MyRaspberryPi/shadow/update/delta"

# Temas a los que se suscribirá el cliente
topics_to_subscribe = [
    "thing/rfid/one",
    "thing/rfid/two",
    "thing/rfid/three"
]

# Callback cuando se conecta al broker
def on_connect(client, userdata, flags, rc, properties=None):
    # rc es el código de respuesta de conexión - Success - Not authorized - se asocia con la Politica de conexión
    print(f"Conectado con el código {rc}")
    client.subscribe(shadow_delta_topic, qos=0)
    print(f"Suscrito al tema {shadow_delta_topic}")
    for topic in topics_to_subscribe:
        client.subscribe(topic, qos=0)
        print(f"Suscrito al tema {topic}")

def on_message(client, userdata, message):
    print(f"Mensaje recibido en el tema {message.topic}: {message.payload.decode()}")
    if message.topic == shadow_delta_topic:
        print("Actualización del shadow recibida:")
        print(message.payload.decode())

# Crear una instancia del cliente MQTT
client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)

# Configurar TLS/SSL
client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=2, ciphers=None)

# Configurar el callback de conexión
client.on_connect = on_connect
client.on_message = on_message

# Conectar al endpoint de AWS IoT
client.connect(mqtt_endpoint, port=8883)

# Función para publicar mensajes
def publish_message(topic, message):
    client.publish(topic, json.dumps(message))

def update_shadow_state(state):
    # Actualizar el estado del shadow
    payload = {
        "state": {
            "reported": state
        }
    }
    publish_message(shadow_update_topic, payload)

# Mantener la conexión abierta
client.loop_start()


try:
    while True:
        # Publicar en todos los temas cada 5 segundos
        for topic in topics_to_subscribe:
            message = {
                "timestamp": time.time(),
                "data": f"Este es un mensaje de prueba del topic: {topic}"
            }
            publish_message(topic, message)
            print(f"Mensaje publicado en {topic}")

        state = {
            "device": {
                "status": "active",
                "uptime": time.time()
            }
        }
        update_shadow_state(state)
        print("Estado del shadow actualizado")

        time.sleep(5)  # Esperar 5 segundos antes de publicar nuevamente

except KeyboardInterrupt:
    print("Interrupción del teclado, cerrando conexión...")
    client.loop_stop()
    client.disconnect()