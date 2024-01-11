from machine import Pin
from time import sleep
from neopixel import NeoPixel

count = 0
pin = Pin(0, Pin.OUT)
pin_power = Pin(2, Pin.OUT)
pin_power.value(1)
switch = Pin(38, Pin.IN)

np = NeoPixel(pin, 1)   
np[0] = (5, 0, 0) 
np.write()
while count < 5:
    if not switch.value():
        np[0] = (0, 5, 0) 
        np.write()
        count += 1
        while not switch.value():
            sleep(0.1)
    else:
        np[0] = (5, 0, 0)
        np.write()

np[0] = (0, 0, 0)
np.write()
print('You have successfully implemented LAB1!')
    
