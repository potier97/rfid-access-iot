# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import gc
#import webrepl
#webrepl.start()
#gc.collect()

import time
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'XXXX'
password = 'XXXX'
mqtt_server = '192.168.1.24'

def connect():
  station = network.WLAN(network.STA_IF)
  if not station.isconnected():
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
      pass
  print('IP address:', station.ifconfig()[0])

#Connect to WiFi
connect()










