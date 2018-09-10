#!/usr/bin/env python

'''
Simple program desinged to add/remove sensors from SmartIoT using pre-coded interface
'''

from smartIoT_Interface import *
import sys

__author__ = "Miguel Angelo Silva"
__email__ = "maps@ua.pt"

# Barometric sensor pressure device
barometricp_id = "pressure1"
barometricp_name = "barometric_pressure"
barometricp_password = "barometricp_secret"
barometricp_description = '{"lat":40.630302, "lon":-8.657506}'
barometricp_stream = "Barometric pressure stream"

# Barometric sensor temperature device
barometrict_id = "temp1"
barometrict_name = "barometric_temperature"
barometrict_password = "barometrict_secret"
barometrict_description = '{"lat":40.630302, "lon":-8.657506}'
barometrict_stream = "Barometric temperature stream"

# 1-wire temperature device
onewire_id = "temp2"
onewire_name = "onewire_temperature"
onewire_password = "onewire_secret"
onewire_description = '{"lat":40.630302, "lon":-8.657506}'
onewire_stream = "Onewire temperature stream"
	
# waste sensor fulness
wastef_id = "waste1"
wastef_name = "waste1_fullness"
wastef_password = "waste_secret"
wastef_description = '{"lat":40.629601, "lon":-8.656472}'
wastef_stream = "Waste container fullness stream"
waste_lat = "Waste container latitude"
waste_lon = "Waste container longitude"

# waste sensor temperature
wastet_id = "waste1"
wastet_name = "waste1_temperature"
wastet_password = "waste_secret"
wastet_description = '{"lat":40.629601, "lon":-8.656472}'
wastet_stream = "Waste container temperature stream"

# waste sensor maximum volume
wastev_id = "waste1"
wastev_name = "waste1_maxVolume"
wastev_password = "waste_secret"
wastev_description = '{"lat":40.629601, "lon":-8.656472}'
wastev_stream = "Waste container maximum volume stream"

# uv sensor uv index
uvsensorui_id = "uvindex"
uvsensorui_name = "uvsensor_uvindex"
uvsensorui_password = "uvindex_secret"
uvsensorui_description = '{"lat":40.629601, "lon":-8.656472}'
uvsensorui_stream = "UV Sensor UV index stream"

# uv sensor ir
uvsensorir_id = "uvir"
uvsensorir_name = "uvsensor_ir"
uvsensorir_password = "uvir_secret"
uvsensorir_description = '{"lat":40.629601, "lon":-8.656472}'
uvsensorir_stream = "UV Sensor IR stream"

# uv sensor visible
uvsensorv_id = "uvvis"
uvsensorv_name = "uvsensor_vis"
uvsensorv_password = "uvindex_secret"
uvsensorv_description = '{"lat":40.629601, "lon":-8.656472}'
uvsensorv_stream = "UV Sensor visible stream"

# co2 sensor
co2sensor_id = "co2_1"
co2sensor_name = "co2_sensor"
co2sensor_password = "co2_secret"
co2sensor_description = '{"lat":40.629601, "lon":-8.656472}'
co2sensor_stream = "CO2 sensor stream"

# Luminaire
lumsensor_id = "luminaire1"
lumsensor_name = "luminaire"
lumsensor_password = "lum_secret"
lumsensor_description = ""
lumsensor_stream = "Luminair stream"

'''
 Simulators
'''
# temp sim
temp_sim_id = "tempsim1"
temp_sim_name = "tempsim1"
temp_sim_password = "tempsim1_secret"
temp_sim_description = '{"lat":40.629601, "lon":-8.656472}'
temp_sim_stream = "Temperature simulator stream"

# press sim
press_sim_id = "presssim1"
press_sim_name = "presssim1"
press_sim_password = "presssim1_secret"
press_sim_description = '{"lat":40.629601, "lon":-8.656472}'
press_sim_stream = "Pressure simulator stream"

# waste sim
waste_sim_id = "wastesim1"
waste_sim_name = "wastesim1"
waste_sim_password = "wastesim1_secret"
waste_sim_description = '{"lat":40.629601, "lon":-8.656472}'
waste_sim_stream = "Waste simulator stream"

# uv sim
uv_sim_id = "uvsim1"
uv_sim_name = "uvsim1"
uv_sim_password = "uvsim1_secret"
uv_sim_description = '{"lat":40.629601, "lon":-8.656472}'
uv_sim_stream = "UV simulator stream"

# sound sim
sound_sim_id = "soundsim1"
sound_sim_name = "soundsim1"
sound_sim_password = "soundsim1_secret"
sound_sim_description = '{"lat":40.629601, "lon":-8.656472}'
sound_sim_stream = "Sound simulator stream"

# people sim
people_sim_id = "peoplesim1"
people_sim_name = "peoplesim1"
people_sim_password = "peoplesim1_secret"
people_sim_description = '{"lat":40.629601, "lon":-8.656472}'
people_sim_stream = "People simulator stream"

# light sim
light_sim_id = "lightsim1"
light_sim_name = "lightsim1"
light_sim_password = "lightsim1_secret"
light_sim_description = '{"lat":40.629601, "lon":-8.656472}'
light_sim_stream = "Light simulator stream"

# Latitude temperature sim
lat_sim_stream = "Latitude simulator stream"


# Longitude temperature sim
lon_sim_stream = "Longitude simulator stream"

'''
Register sensors and their streams  
'''
def add_all():
	token = authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")[1]
	
	# Register barometric sensor
	# pressure
	dev = register_device("https://iot.alticelabs.com", barometricp_id, barometricp_password, token, barometricp_name, barometricp_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, barometricp_id, barometricp_stream)
	# temperature
	dev = register_device("https://iot.alticelabs.com", barometrict_id, barometrict_password, token, barometrict_name, barometrict_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, barometrict_id, barometrict_stream)

	# register onewire sensor
	dev = register_device("https://iot.alticelabs.com", onewire_id, onewire_password, token, onewire_name, onewire_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, onewire_id, onewire_stream)
	
	# register waste
	# fullness
	dev = register_device("https://iot.alticelabs.com", wastef_id, wastef_password, token, wastef_name, wastef_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, wastef_id, wastef_stream)
	create_stream("https://iot.alticelabs.com", token, wastef_id, waste_lat)
	create_stream("https://iot.alticelabs.com", token, wastef_id, waste_lon)
	# temperature
	dev = register_device("https://iot.alticelabs.com", wastet_id, wastet_password, token, wastet_name, wastet_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, wastet_id, wastet_stream)
	# max volume
	dev = register_device("https://iot.alticelabs.com", wastev_id, wastev_password, token, wastev_name, wastev_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, wastev_id, wastev_stream)

	# register uv sensor
	# uv index
	dev = register_device("https://iot.alticelabs.com", uvsensorui_id, uvsensorui_password, token, uvsensorui_name, uvsensorui_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, uvsensorui_id, uvsensorui_stream)
	# ir
	dev = register_device("https://iot.alticelabs.com", uvsensorir_id, uvsensorir_password, token, uvsensorir_name, uvsensorir_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, uvsensorir_id, uvsensorir_stream)
	# visible
	dev = register_device("https://iot.alticelabs.com", uvsensorv_id, uvsensorv_password, token, uvsensorv_name, uvsensorv_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, uvsensorv_id, uvsensorv_stream)
	
	# register co2 sensor
	dev = register_device("https://iot.alticelabs.com", co2sensor_id, co2sensor_password, token, co2sensor_name, co2sensor_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, co2sensor_id, co2sensor_stream)

	# Luminaire
	dev = register_device("https://iot.alticelabs.com", lumsensor_id, lumsensor_password, token, lumsensor_name, lumsensor_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, lumsensor_id, lumsensor_stream)
	# register simulators
	# temp
	dev = register_device("https://iot.alticelabs.com", temp_sim_id, temp_sim_password, token, temp_sim_name, temp_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, temp_sim_id, temp_sim_stream)
	# press
	dev = register_device("https://iot.alticelabs.com", press_sim_id, press_sim_password, token, press_sim_name, press_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, press_sim_id, press_sim_stream)
	# waste
	dev = register_device("https://iot.alticelabs.com", waste_sim_id, waste_sim_password, token, waste_sim_name, waste_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, waste_sim_id, waste_sim_stream)
	# uv
	dev = register_device("https://iot.alticelabs.com", uv_sim_id, uv_sim_password, token, uv_sim_name, uv_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, uv_sim_id, uv_sim_stream)
	# sound
	dev = register_device("https://iot.alticelabs.com", sound_sim_id, sound_sim_password, token, sound_sim_name, sound_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, sound_sim_id, sound_sim_stream)
	# people
	dev = register_device("https://iot.alticelabs.com", people_sim_id, people_sim_password, token, people_sim_name, people_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, people_sim_id, people_sim_stream)
	# light
	dev = register_device("https://iot.alticelabs.com", light_sim_id, light_sim_password, token, light_sim_name, light_sim_description)
	print(dev)
	create_stream("https://iot.alticelabs.com", token, light_sim_id, light_sim_stream)
	# light actuator
	create_stream("https://iot.alticelabs.com", token, light_sim_id, "Lighting Actuator")
	# Lighting actuator subscription
	subs = create_subscription("https://iot.alticelabs.com", token, "Lighting actuator sensor test", "URL of receiver sensor", "server", light_sim_id, "Lighting Actuator", "active", 10, 3600, 5, "30,45,60", "http://putsreq.com/i1EfUj3raw9gJWozF662")
	print(subs)
	# Create latitude stream
	create_stream("https://iot.alticelabs.com", token, temp_sim_id, lat_sim_stream)
	# Create longitude stream
	create_stream("https://iot.alticelabs.com", token, temp_sim_id, lat_sim_stream)

'''
 Remove Streams and devices
'''
def remove_all():
	token = authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")[1]

	# remove barometric->temperature
	rem = remove_stream("https://iot.alticelabs.com", token, barometrict_id, barometrict_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", barometrict_id, token)
	print(rem)

	# remove barometric->pressure
	rem = remove_stream("https://iot.alticelabs.com", token, barometricp_id, barometricp_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", barometricp_id, token)
	print(rem)
	
	# remove uv sensor -> uv index
	rem = remove_stream("https://iot.alticelabs.com", token, uvsensorui_id, uvsensorui_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", uvsensorui_id, token)
	print(rem)
	
	# remove uv sensor -> ir
	rem = remove_stream("https://iot.alticelabs.com", token, uvsensorir_id, uvsensorir_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", uvsensorir_id, token)
	print(rem)
	
	# remove uv sensor -> visible
	rem = remove_stream("https://iot.alticelabs.com", token, uvsensorv_id, uvsensorv_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", uvsensorv_id, token)
	print(rem)
	
	# remove onewire temperature
	rem = remove_stream("https://iot.alticelabs.com", token, onewire_id, onewire_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", onewire_id, token)
	print(rem)
	
	# remove co2 sensor
	rem = remove_stream("https://iot.alticelabs.com", token, co2sensor_id, co2sensor_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", co2sensor_id, token)
	print(rem)
	
	# remove waste stream->fullness
	rem = remove_stream("https://iot.alticelabs.com", token, wastef_id, wastef_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", wastef_id, token)
	print(rem)

	# remove waste stream->temperature
	rem = remove_stream("https://iot.alticelabs.com", token, wastet_id, wastet_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", wastet_id, token)
	print(rem)

	# remove waste stream->volume
	rem = remove_stream("https://iot.alticelabs.com", token, wastev_id, wastev_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", wastev_id, token)
	print(rem)
	
	# remove simulators
	# temp
	rem = remove_stream("https://iot.alticelabs.com", token, temp_sim_id, temp_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", temp_sim_id, token)
	print(rem)
	# press
	rem = remove_stream("https://iot.alticelabs.com", token, press_sim_id, press_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", press_sim_id, token)
	print(rem)
	# waste
	rem = remove_stream("https://iot.alticelabs.com", token, waste_sim_id, waste_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", waste_sim_id, token)
	print(rem)
	# uv
	rem = remove_stream("https://iot.alticelabs.com", token, uv_sim_id, uv_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", uv_sim_id, token)
	print(rem)
	# sound
	rem = remove_stream("https://iot.alticelabs.com", token, sound_sim_id, sound_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", sound_sim_id, token)
	print(rem)
	# people
	rem = remove_stream("https://iot.alticelabs.com", token, people_sim_id, people_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", people_sim_id, token)
	print(rem)
	# light
	rem = remove_stream("https://iot.alticelabs.com", token, light_sim_id, light_sim_stream)
	print(rem)
	rem = remove_device("https://iot.alticelabs.com", light_sim_id, token)
	print(rem)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "python register.py {add|remove}"
	elif sys.argv[1] == 'add':
		add_all()
	elif sys.argv[1] == 'remove':
		remove_all()
	else:
		print "Invalid option"
