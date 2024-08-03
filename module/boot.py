# This file is executed on every boot (including wake-boot from deepsleep)
import os, machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
import config

ssid = config.ssid
password = config.password

def connect():
  station = network.WLAN(network.STA_IF)
  if not station.isconnected():
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
      pass
  print('IP address:', station.ifconfig()[0])

connect()










