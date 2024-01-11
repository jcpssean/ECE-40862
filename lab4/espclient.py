import network
from machine import Timer
import esp32
import time
import socket
import urequests 

# WiFi configuration
SSID = 'NETGEAR10'
PASSWORD = '1a2b3c4d'

# ThingSpeak API & URL
HTTP_HEADERS = {'Content-Type': 'application/json'} 
WRITE_API_KEY = 'JAJVONY1LI47DWQ5'
THINGSPEAK_URL = 'http://api.thingspeak.com/update'
THINGSPEAK_PORT = 80

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('Connected to', SSID)
    print('IP Address:', wlan.ifconfig()[0])


# send data to ThingSpeak
def send_to_thingspeak(temperature, hall):
    readings = {'field1':temperature, 'field2':hall} 
    request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + WRITE_API_KEY, json = readings, headers = HTTP_HEADERS )  
    request.close() 

# timer callback
def timer_callback(timer):
    temperature = esp32.raw_temperature()  # May need calibration
    hall = esp32.hall_sensor()
    print('Temperature:', temperature)
    print('Hall sensor:', hall)
    
    send_to_thingspeak(temperature, hall)


connect_wifi()
# hardware timer
timer = Timer(0)
timer.init(period=30000, mode=Timer.PERIODIC, callback=timer_callback)

# Run for 5 minutes
time.sleep(300)
timer.deinit()