# SI1145 controller
# Based on https://github.com/THP-JOE/Python_SI1145/blob/master/SI1145/SI1145.py
# SI1145 Registers shown here https://www.silabs.com/documents/public/data-sheets/Si1145-46-47.pdf

import smbus
import time

SI1145_ADDR = 0x60
bus = smbus.SMBus(1)

def configure_uvsensor():
	# Reset sensor
	bus.write_byte_data(SI1145_ADDR, 0x08, 0)
	bus.write_byte_data(SI1145_ADDR, 0x09, 0)
	bus.write_byte_data(SI1145_ADDR, 0x04, 0)
	bus.write_byte_data(SI1145_ADDR, 0x05, 0)
	bus.write_byte_data(SI1145_ADDR, 0x06, 0)
	bus.write_byte_data(SI1145_ADDR, 0x03, 0)
	bus.write_byte_data(SI1145_ADDR, 0x21, 0xFF)

	bus.write_byte_data(SI1145_ADDR, 0x18, 0x01)
	time.sleep(.01)
	bus.write_byte_data(SI1145_ADDR, 0x07, 0x17)
	time.sleep(.01)

	# Calibration
	# Enable UVindex measurement coefficients
	bus.write_byte_data(SI1145_ADDR, 0x13, 0x29)
	bus.write_byte_data(SI1145_ADDR, 0x14, 0x89)
	bus.write_byte_data(SI1145_ADDR, 0x15, 0x02)
	bus.write_byte_data(SI1145_ADDR, 0x16, 0x00)
	
	# Enable UV sensor
	write_param(0x01, 0x80 | 0x20 | 0x10 | 0x01)

	# Enable interrupt for every sample
	bus.write_byte_data(SI1145_ADDR, 0x03, 0x01)
	bus.write_byte_data(SI1145_ADDR, 0x04, 0x01)	
	
	# Program led
	bus.write_byte_data(SI1145_ADDR, 0x0F, 0x03)
	write_param(0x07, 0x03)

	# Prox sensor #1 uses LED #1
	write_param(0x02, 0x01)
	
	# Fastest clocks, clock div 1
	write_param(0x0B, 0)
	
	# Take 511 clocks to measure
	write_param(0x0A, 0x70)
	
	# prox mode, high range
	write_param(0x0C, 0x20 | 0x04)
	write_param(0x0E, 0x00)
	
	# Fastest clocks, clock div 1
	write_param(0x1E, 0)
	
	# Take 511 clocks to measure
	write_param(0x1D, 0x70)
	
	# high range mode
	write_param(0x1F, 0x20)
	
	# fastest clocks, clock div 1
	write_param(0x11, 0)
	
	# Take 511 clocks to measure
	write_param(0x10, 0x70)
	
	# in high range mode (not normal signal)
	write_param(0x12, 0x20)

	# measurement rate for auto
	bus.write_byte_data(SI1145_ADDR, 0x08, 0xFF)

	# auto run
	bus.write_byte_data(SI1145_ADDR, 0x18, 0x0F)
	
def write_param(param, vals):
	bus.write_byte_data(SI1145_ADDR, 0x17, vals)
	bus.write_byte_data(SI1145_ADDR, 0x18, param | 0xA0)
	
def get_uvsensor_data():
	vis = bus.read_word_data(0x60, 0x22)
	ir = bus.read_word_data(0x60, 0x24)
	uv = bus.read_word_data(0x60, 0x2C)
	return {'visible': vis,
			'ir': ir,
			'uv':uv/100}