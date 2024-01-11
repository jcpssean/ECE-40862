import machine
from machine import Pin

year = int(input("Year? "))
month = int(input("Month? "))
day = int(input("Day? "))
weekday = int(input("Weekday? "))
hour = int(input("Hour? "))
minute = int(input("Minute? "))
second = int(input("Second? "))
microsecond = int(input("Microsecond? "))

rtc = machine.RTC()
rtc.datetime((year, month, day, weekday, hour, minute, second, microsecond))

def time_callback(t):
    # Timer display callback
    print('Date and Time:', rtc.datetime())

tim = machine.Timer(0)
tim.init(period=30000, mode=machine.Timer.PERIODIC, callback=time_callback)

def switch_handler(p):
    # switch handler to switch mode between freq and duty cycle
    global freq_mode, first_press
    freq_mode = not freq_mode
    #print('freq' if freq_mode else 'duty')
    first_press = False

def pot_read(t):
    # read potentiometer value every 100 ms
    global freq_mode, first_press
    pot_value = adc.read_u16()
    if not first_press:
        if freq_mode:
            new_freq = int(1 + pot_value * 50 / 65535)
            led.freq(new_freq)
        else:
            new_duty = int(1 + pot_value * 1023 / 65535)
            led.duty(new_duty)

adc = machine.ADC(Pin(34, Pin.IN))
switch = Pin(38, Pin.IN)
switch.irq(trigger=Pin.IRQ_FALLING, handler=switch_handler)
led = machine.PWM(Pin(33, Pin.OUT), freq=10, duty=512)
freq_mode = False
first_press = True

tim1 = machine.Timer(1)
tim1.init(period=100, mode=machine.Timer.PERIODIC, callback=pot_read)