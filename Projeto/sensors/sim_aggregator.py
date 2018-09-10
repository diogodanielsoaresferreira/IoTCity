#!/usr/bin/env python

'''
Simple aggregator for sensor simulators
'''

import threading, time, datetime
from publish import publish_sim
from simfunc import *

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

SIM_PERIOD = 5

def read_sim_temp():
	while(1):
		temp = get_temp_sim(-5,5)
		try:
			print(publish_sim('temp', temp))
		except:
			print "Error publishing temperature simulator values"
		time.sleep(SIM_PERIOD)
		
def read_sim_press():
	while(1):
		press = get_pressure_sim(-50,50)
		try:
			print(publish_sim('press', press))
		except:
			print "Error publishing pressure simulator values"
		time.sleep(SIM_PERIOD)
		
def read_sim_waste():
	while(1):
		waste = get_fullness_sim(0,100)
		try:
			print(publish_sim('waste', waste))
		except:
			print "Error publishing waste simulator values"
		time.sleep(SIM_PERIOD)
		
def read_sim_uv():
	while(1):
		uv = get_uv_sim(1,11)
		try:
			print(publish_sim('uv', uv))
		except:
			print "Error publishing UV simulator values"
		time.sleep(SIM_PERIOD)
		
def read_sim_sound():
	while(1):
		sound = get_sound_sim(-15,15)
		try:
			print(publish_sim('sound', sound))
		except:
			print "Error publishing sound simulator values"
		time.sleep(SIM_PERIOD)
		
def read_sim_people():
	while(1):
		people = get_people_sim(0,100)
		try:
			print(publish_sim('people', people))
		except:
			print "Error publishing people simulator values"
		time.sleep(SIM_PERIOD)
		
def read_sim_light():
	while(1):
		light = get_light_sim(-10,30)
		try:
			print(publish_sim('light', light))
		except:
			print "Error publishing light simulator values"
		time.sleep(SIM_PERIOD)

def read_lat():
	while(1):
		lat = get_lat_sim(40,41)
		try:
			print(publish_sim('lat', lat))
		except:
			print "Error publishing latitude simulator values"
		time.sleep(SIM_PERIOD)

def read_lon():
	while(1):
		lon = get_lon_sim(-9,-8)
		try:
			print(publish_sim('lon', lon))
		except:
			print "Error publishing longitude simulator values"
		time.sleep(SIM_PERIOD)

temp_sim_thread = threading.Thread(target=read_sim_temp)
press_sim_thread = threading.Thread(target=read_sim_press)
waste_sim_thread = threading.Thread(target=read_sim_waste)
uv_sim_thread = threading.Thread(target=read_sim_uv)
sound_sim_thread = threading.Thread(target=read_sim_sound)
people_sim_thread = threading.Thread(target=read_sim_people)
light_sim_thread = threading.Thread(target=read_sim_light)
lat_sim_thread = threading.Thread(target=read_lat)
lon_sim_thread = threading.Thread(target=read_lon)

temp_sim_thread.start()
press_sim_thread.start()
waste_sim_thread.start()
uv_sim_thread.start()
sound_sim_thread.start()
people_sim_thread.start()
light_sim_thread.start()
lat_sim_thread.start()
lon_sim_thread.start()