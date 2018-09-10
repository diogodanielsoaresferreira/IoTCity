#!/usr/bin/env python

'''
Simple simulators for various metrics
'''

import random

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

def get_temp_sim(a,b):
	return 15.0+random.uniform(a,b)
	
def get_pressure_sim(a,b):
	return 1050.0+random.uniform(a,b)
	
def get_fullness_sim(a,b):
	return int(random.uniform(a,b))
	
def get_uv_sim(a,b):
	return int(random.uniform(a,b))
	
def get_sound_sim(a,b):
	return 70+int(random.uniform(a,b))
	
def get_people_sim(a,b):
	return int(random.uniform(a,b))
	
def get_light_sim(a,b):
	return int(random.uniform(a,b))

def get_lat_sim(a,b):
	return int(random.uniform(a,b))

def get_lon_sim(a,b):
	return int(random.uniform(a,b))