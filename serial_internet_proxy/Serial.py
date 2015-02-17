import serial

print "start"

## Todo Accept Com port as an argument
port = serial.Serial("COM4", 9600)

## Todo Check for connection
while True:
	hello_world = port.readline()
	print hello_world