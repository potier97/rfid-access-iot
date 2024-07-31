Si esta conectado a una maquina por ssh,  y necesita pasar archivo puede hacerlo con el comando scp, por ejemplo:


```bash
scp -i "llave-privada.pem" "archivo-a-pasar" pi@IP-DISPOSITIVO:/home/pi
```

Donde:
- "llave-privada.pem" es la llave privada que se usa para conectarse a la maquina.
- "archivo-a-pasar" es el archivo que se quiere pasar.
- pi@IP-DISPOSITIVO es el usuario y la ip de la maquina a la que se quiere pasar el archivo.
- /home/pi es la ruta donde se quiere guardar el archivo en la maquina destino.