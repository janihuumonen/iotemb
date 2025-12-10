import network
import time
import rp2
import sys

import machine
import socket

import requests
import json
import os

from machine import I2C, Pin, ADC
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd


CONFIG_FILE = 'config.json'
AP_SSID = "PicoConfig"
AP_PASSWORD = "salasana"
AP_IP = '192.168.4.1'

I2C_ADDR	 = 39
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
#lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

temp = ADC(Pin(27))
adc = ADC(Pin(26))
button = Pin(15, Pin.IN, Pin.PULL_UP)

#KALIBROINTI
a = 22.222
b = -33.56

#NOLLAUS
zero_point = None


# --- HTML-koodi konfigurointisivulle ---
HTML = """
<!DOCTYPE html>
<html>
<head><title>Pico W Konfigurointi</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="utf-8">
</head>
<body>
  <h1>Pico W WLAN Konfigurointi</h1>
  <form action="/save" method="post">
	<label for="ssid">Verkon nimi (SSID):</label><br>
	<input type="text" id="ssid" name="ssid" required><br><br>
	<label for="password">Salasana:</label><br>
	<input type="password" id="password" name="password"><br><br>
	<label for="url">Palvelimen URL:</label><br>
	<input type="text" id="url" name="url"><br><br>
	<input type="submit" value="Tallenna ja Käynnistä Uudelleen">
  </form>
</body>
</html>
"""



# Configuration

def config_found():
	return CONFIG_FILE in os.listdir()

def read_config():
	with open(CONFIG_FILE, encoding='UTF-8') as f:
		return json.loads(f.read())

def write_config(o):
	# Tallentaa uudet tunnukset tiedostoon ja käynnistää laitteen uudelleen.
	try:
		with open(CONFIG_FILE, 'w', encoding='UTF-8') as f:
			f.write(json.dumps(o))
		print("WLAN-tunnukset tallennettu. Käynnistetään uudelleen...")
		time.sleep(4)
		machine.reset() # Käynnistää laitteen uudelleen
	except Exception as e:
		print(f"Virhe tallennuksessa: {e}")

def reset_config():
	try:
		os.remove(CONFIG_FILE)
	except:
		pass
	sys.exit() # or machine.reset()

def check_for_reset():
	# Checked in main loop & connect loop
	return rp2.bootsel_button() == 1



# Network

def connect(ssid,password):
	#Connect to WLAN
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.connect(ssid, password)
	while wlan.isconnected() == False:
		if check_for_reset(): reset_config()
		print('Waiting for connection...')
		time.sleep(1)
	ip = wlan.ifconfig()[0]
	print(f'Connected on {ip}')
	return ip

def send(url,data):
	# Send data to server
	response = requests.post(url,data=data)
	response_code = response.status_code
	response_content = response.content

	# Print results
	print('Response code: ', response_code)
	print('Response content:', response_content)
	return response_code

def setup_access_point():
	# Asettaa Pico W:n Access Point -tilaan.
	wlan = network.WLAN(network.AP_IF)
	wlan.active(True)
	wlan.config(essid=AP_SSID, password=AP_PASSWORD)
	# Asetetaan staattinen IP AP:lle
	wlan.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
	print(f"Access Point käynnistetty: SSID='{AP_SSID}' salasana='{AP_PASSWORD}'")
	print(f"Yhdistä osoitteeseen: http://{AP_IP}")
	return wlan



# --- Palvelinlogiikka ---

def url_decode(s):
	# Yksinkertaistettu URL-dekoodaus: korvaa '+' välilyönnillä ja dekoodaa %-koodaukset.
	s = s.replace('+', ' ')
	parts = s.split('%')
	decoded = parts[0]
	for part in parts[1:]:
		if len(part) >= 2:
			try:
				# Muunnetaan heksadesimaaliluku merkiksi
				char_code = int(part[:2], 16)
				decoded += chr(char_code) + part[2:]
			except ValueError:
				decoded += '%' + part # Jos ei ole validi heksadesimaali, jätetään ennalleen
		else:
			decoded += '%' + part
	return decoded.strip()

def run_ap():
	# 1. Aseta Access Point
	ap = setup_access_point()

	# 2. Avaa Socket-portti
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 80))
	s.listen(5)

	while True:
		try:
			conn, addr = s.accept()
			request = conn.recv(1024).decode()
			print('Saapunut pyyntö:', request)

			# Tarkista, onko kyseessä POST-pyyntö konfigurointitietojen tallentamiseen
			if request.startswith('POST /save'):
				content_start = request.find('\r\n\r\n') + 4
				post_data = request[content_start:]
			
				params = {}
				for pair in post_data.split('&'):
					try:
						key, value_encoded = pair.split('=', 1)
						params[key] = url_decode(value_encoded)
					except ValueError:
						pass

				if 'ssid' in params and 'password' in params:
					print(f"Tallennetaan uudet tunnukset: SSID='{params['ssid']}'")
					write_config(params)
			
				response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Tunnukset tallennettu! Uudelleenkäynnistys käynnissä...</h1>"
		
			else:
				response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + HTML

			conn.sendall(response.encode())
			conn.close()

		except OSError as e:
			conn.close()
			print('Yhteysvirhe:', e)



# Sensor reading

def val2temp(v):
	return (v-13792.101)/728.057
#100k
#m,c=728.0569845666805 13792.101305896282

def read_avg_val(samples, delay):
	total = 0
	for _ in range(samples):
		total += temp.read_u16()
		time.sleep_ms(delay)
	return total / samples

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

def read_data():
	avg_voltage = read_average_voltage(30, 20)
	height = voltage_to_height(avg_voltage)

	#lcd_write(height,avg_voltage)
	#return height
	t = read_avg_val(30,20)
	tstr = f'{val2temp(t):.2f} C'#°C'
	hstr = f'{height:.2f} cm'
	return '   '.join([hstr,tstr])



# LCD

def lcd_write(height,avg_voltage):
	lcd.clear()
	lcd.move_to(0, 0)
	lcd.putstr(f"Height: {height:2.1f}cm")
	lcd.move_to(0, 1)
	lcd.putstr(f"V: {avg_voltage:5.2f} V")



# Calibrate button event handler

def calibrate(pin):
	print("Button Pressed!")
	global zero_point
	zero_point = read_average_voltage(30, 20)
	#lcd.clear()
	#lcd.putstr("NOLLAUS TEHTY")
	time.sleep(1.5)



def run_main(o):
	t = -1
	# Attach the interrupt to the button's falling edge
	button.irq(trigger=Pin.IRQ_FALLING, handler=calibrate)
	# Main loop
	while True:
		if check_for_reset(): reset_config()
		data = read_data()
		if not (t:=t+1)%5 and o.get('url'):
			print(data)
			# TODO: trigger
			send(o['url'], data)
			if t>=10000: t = 0



# Execution starts

#lcd.clear()

if config_found():
	o = read_config()
	if o.get('ssid'):
		ip = connect(o['ssid'], o['password'])
	run_main(o)
else:
	run_ap()

