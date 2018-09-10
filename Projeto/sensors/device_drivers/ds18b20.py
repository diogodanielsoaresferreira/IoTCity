'''
Simple set of functions to extract 1-wire temperature sensor data
'''

# DS18B20 file location
DS18B20_sensor_loc = '/sys/bus/w1/devices/28-0000054ce9d4/w1_slave'

def get_onewire_temp():
	# Open file with sensor data (gets updated roughly every ten seconds)
	file = open(DS18B20_sensor_loc, 'r')
	# Parse file lines
	lines = file.readlines()
	file.close()
	if lines[0].find('YES') != -1: # can read
		#(discard, sep, temp) = lines[1].partition(' t=')
		pos = lines[1].find('=')
		return float(lines[1][pos+1:-1])/1000
	else:
		return None