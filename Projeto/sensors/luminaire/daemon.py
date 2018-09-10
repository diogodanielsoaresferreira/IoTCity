#!/usr/bin/env python

'''
Simple script to receive values and send them to a luminaire
Running on a Raspberry Pi 2
'''

from luminaire import get_dimming_value, set_dimming_value
from smartIoT_Interface import *
import time

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

DEVICE_ID = "server"
DEVICE_PASSWORD = "debug_mode"
LIGHTING_SUBID = "8acbf27b-4841-4c2b-b7d4-12bc8588b74b"

i = 0

while True:
	try:
		if (i == 0):
			print "30s are up, going to authenticate"
			token = authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")[1]
			auth = device_authentication("https://iot.alticelabs.com", DEVICE_ID, DEVICE_PASSWORD)[1]
			print "Authentication successful"
			
		print "Retrieving subscription values"
		ret = retrieve_subscription_values("https://iot.alticelabs.com", auth, LIGHTING_SUBID)
		content = json.loads(ret[1])["values"]
		if content:
			print "Stream had values, getting the most recent"
			dimming = content[len(content)-1]["data"]
			print "Setting most recent dimming value: " + dimming
			set_dimming_value(dimming)
		else:
			print "Stream was empty"
		i = (i+1) % 30
		time.sleep(1)

	except Exception as e:
		print "error"
