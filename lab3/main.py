import network
import ntptime
import time
from machine import RTC, Timer, TouchPad, Pin, deepsleep, wake_reason, reset_cause, DEEPSLEEP_RESET
from neopixel import NeoPixel
from esp32 import wake_on_ext0, WAKEUP_ANY_HIGH

# WiFi configuration
SSID = 'Sean'
PASSWORD = '01010101'

# pin setup
touch_pin = TouchPad(Pin(14, Pin.IN))
led = Pin(13, Pin.OUT)
led.on()
np_power = Pin(2, Pin.OUT)
np_power.value(1)
np = NeoPixel(Pin(0, Pin.OUT), 1)  # Pin 0, 1 pixel
switch = Pin(37, Pin.IN)
wake_on_ext0(switch, WAKEUP_ANY_HIGH)

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
    
def dst_start_date():
    year = time.localtime()[0]
    d = time.localtime(time.mktime((year,3,1,0,0,0,0,0)))[6]
    return 14 - d

def dst_end_date():
    year = time.localtime()[0]
    n = time.localtime(time.mktime((year,11,1,0,0,0,0,0)))[6]
    return 7 - n

# rtc timer callback
def rtc_timer_callback(t):
    year, month, day, _, hour, minute, second, _ = rtc.datetime()
    
    # get dst range
    dst_start = (3, dst_start_date())
    dst_end = (11, dst_end_date())
    
    
    if (month, day) >= dst_start and (month, day) < dst_end:
        # dst adjustment
        if rtc.datetime()[4] < 4:
            print('Date: {:02}/{:02}/{:4}'.format(rtc.datetime()[1], rtc.datetime()[2]-1, rtc.datetime()[0]))
            print('Time: {:02}:{:02}:{:02} HRS'.format((rtc.datetime()[4]+20), rtc.datetime()[5], rtc.datetime()[6]))
        else:
            print('Date: {:02}/{:02}/{:4}'.format(rtc.datetime()[1], rtc.datetime()[2], rtc.datetime()[0]))
            print('Time: {:02}:{:02}:{:02} HRS'.format(rtc.datetime()[4]-4, rtc.datetime()[5], rtc.datetime()[6]))
    else:
        if rtc.datetime()[4] < 5:
            print('Date: {:02}/{:02}/{:4}'.format(rtc.datetime()[1], rtc.datetime()[2]-1, rtc.datetime()[0]))
            print('Time: {:02}:{:02}:{:02} HRS'.format((rtc.datetime()[4]+20), rtc.datetime()[5], rtc.datetime()[6]))
        else:
            print('Date: {:02}/{:02}/{:4}'.format(rtc.datetime()[1], rtc.datetime()[2], rtc.datetime()[0]))
            print('Time: {:02}:{:02}:{:02} HRS'.format(rtc.datetime()[4]-5, rtc.datetime()[5], rtc.datetime()[6]))

# touch timer callback
def touch_timer_callback(t):
    touch_value = touch_pin.read()
    if touch_value < 600:
        np[0] = (0, 5, 0)  # Green
    else:
        np[0] = (0, 0, 0)  # Off
    np.write()

# deep sleep timer callback
def deep_sleep_timer_callback(t):
    print("Going to sleep for 1 minute...")
    led.off()  # turn off red LED 
    deepsleep(60000)  # deepsleep 10 sec


if reset_cause() == DEEPSLEEP_RESET:
    
    # Check wake up reason
    wake_up_reason = wake_reason()
    if wake_up_reason == 2: 
        print("\nWoke up due to EXT0 wake-up")
    else:
        print("\nWoke up due to timer wake-up")

connect_wifi()
rtc = RTC()
ntptime.settime()

rtc_timer = Timer(0)
rtc_timer.init(period=15000, mode=Timer.PERIODIC, callback=rtc_timer_callback)

touch_timer = Timer(1)
touch_timer.init(period=50, mode=Timer.PERIODIC, callback=touch_timer_callback)

deep_sleep_timer = Timer(2)
deep_sleep_timer.init(period=30000, mode=Timer.PERIODIC, callback=deep_sleep_timer_callback)


