import time
from machine import I2C, Pin, ADC
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd


I2C_ADDR     = 39
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

adc = ADC(Pin(26))
button = Pin(15, Pin.IN, Pin.PULL_UP)

#KALIBROINTI
a = 22.222
b = -33.56

#NOLLAUS
zero_point = None
lcd.clear()

def read_average_voltage(samples, delay):
    total = 0
    for _ in range(samples):
        total += adc.read_u16()
        time.sleep_ms(delay)
    return total / samples * 3.3 / 65535

def voltage_to_height(voltage):
    if zero_point is None:
        height = a * voltage + b
    else:
        delta_v = voltage - zero_point
        height = delta_v * a
    return round(height, 1)

def check_button():
    global zero_point
    if button.value() == 0:
        if button.value() == 0:
            zero_point = read_average_voltage(30, 20)
            lcd.clear()
            lcd.putstr("NOLLAUS TEHTY")
            time.sleep(1.5)
            return True
    return False

while True:
    
    if check_button():
        continue
    
    avg_voltage = read_average_voltage(30, 20)
    height = voltage_to_height(avg_voltage)
    
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(f"Height: {height:2.1f}cm")
    lcd.move_to(0, 1)
    lcd.putstr(f"V: {avg_voltage:5.2f} V")
    


