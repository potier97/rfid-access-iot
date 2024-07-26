<p align="center">
  <a href="http://nipoanz.com/" target="blank"><img src="./assets/image-6.png" width="300" alt="NPA Logo" /></a>
</p>

# Rfid Iot Project

Este proyecto tiene como objetivo controlar el acceso a una puerta utilizando un sistema RFID, un ESP8266 y una arquitectura en la nube a través de AWS IoT Core. Inicialmente, el proyecto se configura para conectar con un broker MQTT (Mosquitto) en una Raspberry Pi. Posteriormente, se implementará en la nube de AWS.

## Instalar
1. Clonar el repositorio:
    ```sh
    git clone https://github.com/potier97/rfid-access-iot.git
    cd rfid-access-iot
    ```

2. Crear y activar el entorno virtual:
    ```sh
    python -m venv env
    # En Windows
    .\env\Scripts\activate
    # En macOS y Linux
    source env/bin/activate
    ```

3. Instalar dependencias:
    ```sh
    pip install -r requirements.txt
    ```


## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos](#requisitos)
3. [Instalación del Broker Mosquitto](#instalación-del-broker-mosquitto)
4. [Ampy - Transferencia de Archivos](#ampy---transferencia-de-archivos)
5. [Configuración Inicial del ESP8266](#configuración-inicial-del-esp8266)
6. [Control del Servo mediante MQTT](#control-del-servo-mediante-mqtt)
7. [Migración a AWS IoT Core](#migración-a-aws-iot-core)
8. [Contribuciones](#contribuciones)
9. [Licencia](#licencia)


---
## Introducción
El proyecto `RFID Access IoT` permite gestionar el acceso a una puerta utilizando tarjetas RFID. La información de acceso se gestiona a través de un **ESP8266** que se comunica con un **broker MQTT** alojado en una Raspberry Pi y, en futuras versiones, con AWS IoT Core.


---
## Requisitos
 - Raspberry Pi con Raspbian instalado
 - ESP8266 con MicroPython
 - Módulo RFID (MFRC522)
 - Servomotor
 - Tarjetas RFID
 - Mosquitto instalado en la Raspberry Pi
 - Conexión a Internet

---
## Instalación del Broker Mosquitto

1. Instalar Mosquitto:
    
    ```sh
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y mosquitto mosquitto-clients
    ```

2. Iniciar el servicio de Mosquitto:
    
    ```sh
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    ```

3. Comprobar que el servicio está en ejecución:
    
    ```sh
    sudo systemctl status mosquitto
    ```

4. Hacer pruebas de conexión con el broker:
    En una terminal, suscribirse a un tópico:

    ```sh
    mosquitto_sub -h localhost -t test
    ```

    En otra terminal, publicar un mensaje en el tópico:

    ```sh
    mosquitto_pub -h localhost -t test -m "Hello, world!"
    ```

    > Deberías ver el mensaje en la terminal donde te suscribiste al tópico.

<br>
<p align="center" >
  <a href="http://nipoanz.com/" target="blank">
  <img src="./assets/image.png" alt="image" />
  </a>
</p>

---
## Ampy - Transferencia de Archivos

Para transferir archivos al ESP8266, utilizaremos `ampy`. Para instalarlo, ejecuta el siguiente comando:
```sh
pip install adafruit-ampy
```

- Para verificar que `ampy` se instaló correctamente, ejecuta el siguiente comando:
```sh
ampy --help
```

- Trasferir archivos al ESP8266:
```sh
ampy --port com6 put main.py
```

- Obtener la lista de archivos en el ESP8266:
```sh
ampy --port com6 ls
```

- Obtener un archivo del ESP8266:
```sh
ampy --port com6 get main.py
```

- Eliminar un archivo del ESP8266:
```sh
ampy --port com6 rm main.py
```

