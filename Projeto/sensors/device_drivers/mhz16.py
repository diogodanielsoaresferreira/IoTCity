# MH-Z16 controller
# Based on https://github.com/OpenAgInitiative/openag_mhz16_python

import smbus
import time

MHZ16_ADDR  = 0x4D
bus         = smbus.SMBus(1)
cmd_measure = [0xFF,0x01,0x9C,0x00,0x00,0x00,0x00,0x00,0x63]
IOCONTROL   = 0X0E << 3
FCR         = 0X02 << 3
LCR         = 0X03 << 3
DLL         = 0x00 << 3
DLH         = 0X01 << 3
THR         = 0X00 << 3
RHR         = 0x00 << 3
TXLVL       = 0X08 << 3
RXLVL       = 0X09 << 3

def configure_co2sensor():
	try:
		write_to_register(IOCONTROL, 0x08)
	except IOError:
		pass
		
	write_to_register(FCR, 0x07)
	write_to_register(LCR, 0x83)
	write_to_register(DLL, 0x60)
	write_to_register(DLH, 0x00)
	write_to_register(LCR, 0x03)
	
def get_co2sensor_data():
	write_to_register(FCR, 0x07)
	if read_from_register(TXLVL) >= len(cmd_measure):
		bus.write_i2c_block_data(MHZ16_ADDR, THR, cmd_measure)
	return parse(receive())
	
def parse(response):
	checksum = 0
	result = 0
	if len(response) < 9:
		return

	for i in range (0, 9):
		checksum += response[i]

	if response[0] == 0xFF:
		if response[1] == 0x9C:
			if checksum % 256 == 0xFF:
				result = (response[2]<<24) + (response[3]<<16) + (response[4]<<8) + response[5]

	return result
	
def receive():
	n     = 9
	buf   = []
	start = time.clock()
        
	while n > 0:
		rx_level = read_from_register(RXLVL)
            
		if rx_level > n:
			rx_level = n

		buf.extend(bus.read_i2c_block_data(MHZ16_ADDR, RHR, rx_level))
		n = n - rx_level

		if time.clock() - start > 0.2:
			break

	return buf
		
def write_to_register(register, val):
	time.sleep(0.001)
	bus.write_byte_data(MHZ16_ADDR, register, val)

def read_from_register(register):
	time.sleep(0.005)
	return bus.read_byte_data(MHZ16_ADDR, register)