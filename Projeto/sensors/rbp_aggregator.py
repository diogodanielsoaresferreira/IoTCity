#!/usr/bin/env python

'''
Simple aggregator designed to read various sensors connected to a Raspberry Pi
and send their data to a broker.

Working sensors: Barometric (BMP180), 1-wire temperature (DS18B20), UV radiation sensor (SI1145), CO2 sensor (MHZ16)
'''

from device_drivers.bmp180 import get_barometric_data
from device_drivers.ds18b20 import get_onewire_temp
from device_drivers.si1145 import get_uvsensor_data, configure_uvsensor
from device_drivers.mhz16 import get_co2sensor_data, configure_co2sensor
import threading, time, datetime, os
from publish import *

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

BAROM_PERIOD   = 30  # in seconds
TEMP_PERIOD    = 30  # in seconds
UV_PERIOD 	   = 30  # in seconds
CO2_PERIOD 	   = 30  # in seconds

# Load DS18B20 kernel modules
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Configure SI1145
configure_uvsensor()

# Configure MHZ16
configure_co2sensor()

# Barometric sensor thread function
def read_barom():
	while(1):
		try:
			barom = get_barometric_data()
		except:
			print 'Error getting barometric sensor data'
		
		try:
			print publish_barom('temp', barom['temperature'])
			print publish_barom('pres', barom['pressure'])
		except:
			print 'Error publishing barometric data'
		time.sleep(BAROM_PERIOD)

# 1-wire temperature sensor thread function
def read_onewire():
	while(1):
		try:
			temp = get_onewire_temp()
		except:
			print 'Error getting onewire sensor data'
		try:
			if temp != None:
				# SmartIoT
				print publish_onewire(temp)
			else:
				print 'Invalid onewire temperature value'
		except:
			print 'Error publishing onewire data'
		time.sleep(TEMP_PERIOD)
		
# UV sensor thread function
def read_uvsensor():
	while(1):
		try:
			uvsens = get_uvsensor_data()
		except:
			print 'Error getting uv sensor data'
		# SmartIoT
		try:
			print publish_uvsensor('uidx', uvsens['uv'])
			print publish_uvsensor('ir', uvsens['ir'])
			print publish_uvsensor('vis', uvsens['visible'])
		except:
			print 'Error publishing uv data'
		time.sleep(UV_PERIOD)
		
# CO2 sensor thread function
def read_co2sensor():
	while(1):
		try:
			co2 = get_co2sensor_data()
		except:
			print 'Error getting CO2 sensor data'
		# SmartIoT
		try:
			print publish_co2(co2)
		except:
			print 'Error publishing CO2 data'
		time.sleep(CO2_PERIOD)

# Starting the threads
bar_thread = threading.Thread(target=read_barom)
onewire_thread = threading.Thread(target=read_onewire)
uv_thread = threading.Thread(target=read_uvsensor)
co2_thread = threading.Thread(target=read_co2sensor)
bar_thread.start()
onewire_thread.start()
uv_thread.start()
co2_thread.start()
