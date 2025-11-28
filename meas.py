import machine as mac
import time

ad = mac.ADC(26) # GP26_A0

def r():
	res = []
	for _ in range(0,20):
		res.append(ad.read_u16())
		time.sleep(0.1)
	return int( sum(res)/len(res) )

#GP shorted to | value from read_u16()
# AGND 144
# 3V3 65535
