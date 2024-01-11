import network
from machine import Timer, Pin
import esp32
import socket

red_led = Pin(13, Pin.OUT)

# Global variables
temp = esp32.raw_temperature()
hall = esp32.hall_sensor()
red_led_state = "ON" if red_led.value() else "OFF"

# WiFi configuration
SSID = 'NETGEAR10'
PASSWORD = '1a2b3c4d'

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

def web_page():
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    temp, hall, red_led_state
    """
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h1 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h1>ESP32 WEB Server</h1>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="sensor-labels">Temperature</span> 
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p>
    <a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage

def timer_callback(timer):
    global temp, hall, red_led_state
    temp = esp32.raw_temperature()
    hall = esp32.hall_sensor()
    red_led_state = "ON" if red_led.value() else "OFF"


addr = socket.getaddrinfo('192.168.1.6', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

timer = Timer(0)
timer.init(period=50, mode=Timer.PERIODIC, callback=timer_callback)

connect_wifi()

while True:
    cl, addr = s.accept()
    request = cl.recv(1024)
    request = str(request)
    
    # check button click
    red_led_off = request.find('/?red_led=off')
    red_led_on = request.find('/?red_led=on')
    if red_led_off == 6:
        print('LED OFF')
        red_led.off()
        red_led_state = "OFF"
    if red_led_on == 6:
        print('LED ON')
        red_led.on()
        red_led_state = "ON"
    
    # get HTML content
    response = web_page()
    
    # send HTTP response
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.sendall(response)
    
    cl.close()
