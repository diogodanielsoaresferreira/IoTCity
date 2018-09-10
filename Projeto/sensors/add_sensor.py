#!/usr/bin/env python

'''
	Script to add sensors and streams to IoTCity
'''

import sys, json, requests

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

URL = "http://193.136.92.216:5010"

def add_sensor(json_file):
	try:
		json_file = open(json_file)
		json_data = json.load(json_file)
	except:
		print "Could not load config file"
		return

	try:
		device_data = { "id": json_data["sensor_id"],
				"password": json_data["sensor_passwd"],
				"name": json_data["sensor_name"],
				"description": json_data["sensor_description"],
				"type": json_data["sensor_type"],
				"lat": json_data["sensor_lat"],
				"lon": json_data["sensor_lon"]}
	except:
		print "Invalid json file format"
		return

	# Add sensor
	try:
		resp = requests.post(URL+"/ws/addsensor", json=device_data)
	except:
		print "Could not contact server"
		return
	
	resp_json = resp.json()
	if resp_json["status"] == "Error":
		print resp_json["info"]
		return
	else:
		print "Sensor "+json_data["sensor_id"]+" added successfully"

	# Add streams
	for stream in json_data["sensor_streams"]:
		try:
			stream_data = { "sensor_id": json_data["sensor_id"],
					"subtype": stream["stream_subtype"],
					"sub_name": stream["stream_name"],
					"sub_description": stream["stream_description"]}
		except:
			print "Invalid json file format"
			return
		try:
			resp = requests.post(URL+"/ws/addsubscription", json=stream_data)
		except:
			print "Could not contact server"
			return

		resp_json = resp.json()
		if resp_json["status"] == "Error":
			print resp_json["info"]
			return
		else:
			print "Stream "+stream["stream_name"]+" added successfully"

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: python add_sensor.py {file}"
	else:
		add_sensor(sys.argv[1])
