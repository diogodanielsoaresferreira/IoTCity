#!/usr/bin/env python

'''
	Set of functions to publish data into streams
'''

from smartIoT_Interface import *
import datetime, sys, pytz

# Timezone
zone = 'Europe/Lisbon'

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

def publish_sim(sim, value):
	if sim == 'temp':
		temp_sim_auth = device_authentication("https://iot.alticelabs.com", temp_sim_id, temp_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", temp_sim_auth, temp_sim_id, temp_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_temp', value, pub[1]
	if sim == 'press':
		press_sim_auth = device_authentication("https://iot.alticelabs.com", press_sim_id, press_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", press_sim_auth, press_sim_id, press_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_press', value, pub[1]
	if sim == 'waste':
		waste_sim_auth = device_authentication("https://iot.alticelabs.com", waste_sim_id, waste_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", waste_sim_auth, waste_sim_id, waste_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_waste', value, pub[1]
	if sim == 'uv':
		uv_sim_auth = device_authentication("https://iot.alticelabs.com", uv_sim_id, uv_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", uv_sim_auth, uv_sim_id, uv_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_uv', value, pub[1]
	if sim == 'sound':
		sound_sim_auth = device_authentication("https://iot.alticelabs.com", sound_sim_id, sound_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", sound_sim_auth, sound_sim_id, sound_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_sound', value, pub[1]
	if sim == 'people':
		people_sim_auth = device_authentication("https://iot.alticelabs.com", people_sim_id, people_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", people_sim_auth, people_sim_id, people_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_people', value, pub[1]
	if sim == 'light':
		light_sim_auth = device_authentication("https://iot.alticelabs.com", light_sim_id, light_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", light_sim_auth, light_sim_id, light_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_light', value, pub[1]
	if sim == 'lat':
		lat_sim_auth = device_authentication("https://iot.alticelabs.com", temp_sim_id, temp_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", lat_sim_auth, temp_sim_id, lat_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_lat', value, pub[1]
	if sim == 'lon':
		lon_sim_auth = device_authentication("https://iot.alticelabs.com", temp_sim_id, temp_sim_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", lon_sim_auth, temp_sim_id, lon_sim_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'sim_lon', value, pub[1]

def publish_barom(stream, value):
	# Authenticate barometric sensor
	if stream == 'temp':
		baromt_auth = device_authentication("https://iot.alticelabs.com", barometrict_id, barometrict_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", baromt_auth, barometrict_id, barometrict_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'temp_baro', value, pub[1]
	if stream == 'pres':
		baromp_auth = device_authentication("https://iot.alticelabs.com", barometricp_id, barometricp_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", baromp_auth, barometricp_id, barometricp_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'press_baro', value, pub[1]

def publish_onewire(value):
	# Authenticate 1-wire sensor
	onewire_auth = device_authentication("https://iot.alticelabs.com", onewire_id, onewire_password)[1]
	pub = publish_into_stream("https://iot.alticelabs.com", onewire_auth, onewire_id, onewire_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
	return 'temp_onewire', value, pub[1]
	
def publish_waste(stream, value):
	# Authenticate waste sensor
	if stream == 'fullness':
		wastef_auth = device_authentication("https://iot.alticelabs.com", wastef_id, wastef_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", wastef_auth, wastef_id, wastef_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'waste1_fullness', value, pub[1], datetime.datetime.now(pytz.timezone(zone)).isoformat()
	if stream == 'lat':
		wastef_auth = device_authentication("https://iot.alticelabs.com", wastef_id, wastef_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", wastef_auth, wastef_id, waste_lat, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'waste1_lat', value, pub[1]
	if stream == 'lon':
		wastef_auth = device_authentication("https://iot.alticelabs.com", wastef_id, wastef_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", wastef_auth, wastef_id, waste_lon, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'waste1_lon', value, pub[1]
	if stream == 'temp':
		wastet_auth = device_authentication("https://iot.alticelabs.com", wastet_id, wastet_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", wastet_auth, wastet_id, wastet_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'waste1_temperature', value, pub[1]
	if stream == 'volume':
		wastev_auth = device_authentication("https://iot.alticelabs.com", wastev_id, wastev_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", wastev_auth, wastev_id, wastev_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'waste1_volume', value, pub[1]
		
def publish_uvsensor(stream, value):
	# Authenticate barometric sensor
	if stream == 'uidx':
		uvsensorui_auth = device_authentication("https://iot.alticelabs.com", uvsensorui_id, uvsensorui_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", uvsensorui_auth, uvsensorui_id, uvsensorui_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'uv_index', value, pub[1]
	if stream == 'ir':
		uvsensorir_auth = device_authentication("https://iot.alticelabs.com", uvsensorir_id, uvsensorir_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", uvsensorir_auth, uvsensorir_id, uvsensorir_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'ir', value, pub[1]
	if stream == 'vis':
		uvsensorv_auth = device_authentication("https://iot.alticelabs.com", uvsensorv_id, uvsensorv_password)[1]
		pub = publish_into_stream("https://iot.alticelabs.com", uvsensorv_auth, uvsensorv_id, uvsensorv_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
		return 'visible', value, pub[1]
		
def publish_co2(value):
	# Authenticate co2 sensor
	co2_auth = device_authentication("https://iot.alticelabs.com", co2sensor_id, co2sensor_password)[1]
	pub = publish_into_stream("https://iot.alticelabs.com", co2_auth, co2sensor_id, co2sensor_stream, datetime.datetime.now(pytz.timezone(zone)).isoformat(), value, 300)
	return 'co2 value', value, pub[1]
