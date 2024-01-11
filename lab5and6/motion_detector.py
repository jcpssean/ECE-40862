from neopixel import NeoPixel
import time
from machine import RTC, Timer, Pin, SoftI2C, I2C
from time import sleep
import urequests
import network
import machine

np_power = Pin(2, Pin.OUT)
np_power.value(1)
np = NeoPixel(Pin(0, Pin.OUT), 1)  # Pin 0, 1 pixel
np[0] = (0, 0, 0)
np.write()
red_led = Pin(13, Pin.OUT)
red_led.value(0)

# WiFi configuration
SSID = 'NETGEAR10'
PASSWORD = '1a2b3c4d'

class accel():
    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))
        self.iic.stop()

    def get_raw_values(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        self.iic.stop()
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self):
        raw_ints = self.get_raw_values()
        vals = {}
        vals["AcX"] = self.bytes_toint(raw_ints[0], raw_ints[1])/ 16384 * 9.8
        vals["AcY"] = self.bytes_toint(raw_ints[2], raw_ints[3])/ 16384 * 9.8
        vals["AcZ"] = self.bytes_toint(raw_ints[4], raw_ints[5])/ 16384 * 9.8
#         vals["Tmp"] = self.bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
#         vals["GyX"] = self.bytes_toint(raw_ints[8], raw_ints[9])
#         vals["GyY"] = self.bytes_toint(raw_ints[10], raw_ints[11])
#         vals["GyZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])
        return vals  # returned in range of Int16
        # -32768 to 32767

from machine import SoftI2C, Pin
i2c = SoftI2C(scl=Pin(14), sda=Pin(22))
mpu = accel(i2c)

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
    
    
def send_notification():
    send_data = {'value1': str(mpu.get_values()['AcX'] + x_offset), 'value2': str(mpu.get_values()['AcY'] + y_offset), 'value3': str(mpu.get_values()['AcZ'] + z_offset)}
    req_headers = {'Content-Type': 'application/json'}
    req = urequests.post('https://maker.ifttt.com/trigger/sensor_moved/with/key/cuj-TOA7t36ZdGk-lKIOLs', json=send_data, headers=req_headers)
    req.close()
    

def device_state_callback(t):
    global device_state
    state_get = urequests.get('https://api.thingspeak.com/channels/2360611/fields/1.json?api_key=8QZGI7JWS4YJH8RQ&results=2').json()
    state_data = state_get['feeds'][1]['field1']
#     print(state_data)
    if state_data == "1":
        np[0] = (0, 5, 0)
        np.write()
        if device_state == 1:
            pass
        else:
            mpu_timer.init(period=100, mode=Timer.PERIODIC, callback=mpu_read)
            device_status = 1
    elif state_data == "0":
        mpu_timer.deinit()
        np[0] = (0, 0, 0)
        np.write()
        red_led.value(0)

def mpu_read(t):
    if ((mpu.get_values()['AcX'] + x_offset) > 8) or ((mpu.get_values()['AcX'] + x_offset) < -8) or ((mpu.get_values()['AcY'] + y_offset) > 8) or ((mpu.get_values()['AcY'] + y_offset) < -8) or ((mpu.get_values()['AcZ'] + z_offset) > 15) or ((mpu.get_values()['AcZ'] + z_offset) < -15):
        red_led.value(1)
        send_notification()
    else:
        red_led.value(0)

def calibration():
    x = []
    y = []
    z = []
    print('Please lay the mpu sensor flat for calibration')
    cal = input('Press y when ready (y)')
    if cal == 'y':
        for i in range(50):
            x.append(mpu.get_values()['AcX'])
            y.append(mpu.get_values()['AcY'])
            z.append(mpu.get_values()['AcZ'])
            sleep(0.1)
        print('Calibration finished!')
        return 0-sum(x)/50, 0-sum(y)/50, 9.8-sum(z)/50



# Global variable
device_state = 0

connect_wifi()
x_offset, y_offset, z_offset = calibration()

device_state_timer = Timer(1)
mpu_timer = Timer(2)
calibrate_timer = Timer(0)
device_state_timer.init(period=30000, mode=Timer.PERIODIC, callback=device_state_callback)