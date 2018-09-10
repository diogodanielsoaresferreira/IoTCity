# -*- coding: utf-8 -*-

import json, requests, time
from publish import publish_waste

__author__ = "José Pedro Castanheira"
__email__  = "jp.castanheira@ua.pt"

SLEEP_TIME = 30 # in seconds
URL = "https://manager.360waste.pt/manager/getallsensors?wsuid=4f5fd78616784e36f31cf275cfc5e6f4a17072cdd600e9a00d03bb3890c1e0e8763d67b233dc9d3b5717d6b01207068517153f79d542b4dc3389a0bf11ce4cds&wsid=MxBp2lZMApZJFux"

def read_WasteSensor():
	while(1):
		try:
			response = requests.get(URL)
			data = json.loads(response.text)
		except Exception:
			print "Error getting waste data"
			time.sleep(SLEEP_TIME)
			continue
			
		for key in data:
			if(type(data[key]) is list):
				d = data[key][0]
				maxVolume = d['maxVolume']
				fullness = float(d['volume'])/maxVolume*100
				temperature = d['temperature']
				lat = d['latitude']
				lon = d['longitude']

		try:
			print publish_waste('fullness', fullness)
			print publish_waste('temp', temperature)
			print publish_waste('volume', maxVolume)
			print publish_waste('lat', lat)
			print publish_waste('lon', lon)
		except Exception:
			print "Error publishing waste data"
			
		time.sleep(SLEEP_TIME)

if __name__ == "__main__":
	read_WasteSensor()
