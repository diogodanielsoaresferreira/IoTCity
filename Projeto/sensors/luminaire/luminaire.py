#!/usr/bin/env python

'''
Simple interface for globaltronic luminaires
'''

import requests, sys

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

BRANCH = "1214"
LUMINAIRE = "60"
URL = "http://10.0.0.1/api/"

def set_dimming_value(value):
	resplen = 0
	while resplen == 0:
		resp = requests.post(URL+BRANCH+"/"+LUMINAIRE+"/dimming", json = {"values":value})
		resplen = len(resp.json())
	return {'dimming':resp.json()['dimming']}

def get_dimming_value():
	resplen = 0
	while resplen == 0:
		resp = requests.get(URL+BRANCH+"/"+LUMINAIRE+"/dimming")
		resplen = len(resp.json())
	return {'dimming':resp.json()['dimming']}

if __name__ == '__main__':
	if len(sys.argv) == 2 and sys.argv[1] == 'get':
		print get_dimming_value()
	elif len(sys.argv) == 3 and sys.argv[1] == 'set':
		print set_dimming_value(sys.argv[2])
	else:
		print "Usage: python luminaire.py {set|get} {value}\nset   - to set a dimming value\nget   - to get dimming value \nvalue - integer value [0-100]"
