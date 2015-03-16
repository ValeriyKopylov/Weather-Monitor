#!/usr/bin/env python

import sys
import getopt
import SocketServer
import json
import time
import datetime
import math
import serial
from threading import Thread

BigJsonPacket = []

StopSerialListener = False
# Packet structure
# --------------------------------------------------------------------------------
# | 16 bit outpost_id | 32 bit(float) temp | 32 bit(float) CO | 16 bit(uint) Lux |
# --------------------------------------------------------------------------------
# float sends as 16 bit integral and 16 bit fractional part
# total length 16 + 32 + 32 + 16 = 96 bit = 12 bytes
def listenSerialAndAccumulateData(arg, speed):
    serial_connection = serial.Serial(arg, speed)
    log('Serial connection opened')
    PacketLen = 0x12
    def findNumberOfDigits(number):
        if (number == 0):
            return 0
        digitCntr = 1
        while(True):
            intFract = divmod(number, 10)
            if (intFract[0] == 0):
                return digitCntr
            number = intFract[0]
            digitCntr = digitCntr + 1
    
    while(StopSerialListener == False):
        sensorData = serial_connection.read(PacketLen)
        sensorData = list(bytearray(sensorData))
        outId = sensorData[0] + (sensorData[1] << 8)
        tempI = sensorData[2] + (sensorData[3] << 8) 
        tempF = sensorData[4] + (sensorData[5] << 8)
        coI = sensorData[6] + (sensorData[7] << 8)
        coF = sensorData[8] + (sensorData[9] << 8)
        luxI = sensorData[10] + (sensorData[11] << 8)
        luxF = sensorData[12] + (sensorData[13] << 8)
        humI = sensorData[14] + (sensorData[15] << 8)
        humF = sensorData[16] + (sensorData[17] << 8)
        
        temp = tempI + tempF / (math.pow(10, findNumberOfDigits(tempF)))
        co = coI + coF / (math.pow(10, findNumberOfDigits(coF)))
        lux = luxI + luxF / (math.pow(10, findNumberOfDigits(luxF)))
        hum = humI + humF / (math.pow(10, findNumberOfDigits(humF)))
        # TODO add time here
        jsonString = '{0} {1} {2} {3} {4}'.format(outId, temp, co, lux, hum)
        print jsonString
        BigJsonPacket.append(jsonString)

def log(message):
    print '[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), message)
    sys.stdout.flush()


class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            log('Incoming request from %s:%s' % self.client_address)
            request = self.request.recv(1024).strip()
            log('Incoming request: ' + request)
            
            # send sensorData
            #self.request.sendall(BigJsonPacket)
            log('Response sent to Ethernet')
        except Exception, e:
            log("Exception while receiving message: " + str(e))


def print_usage():
    print """\
Carrier Proxy arguments:
./serial.py [-i|--ip] <ip address> [-p|--port] <port>

Example:
./serial.py --ip 127.0.0.1 --port 4242
"""


def parse_command_line(arguments):
    ip = ''
    port = 0
    try:
        opts, args = getopt.getopt(arguments,
                                   'hi:p:',
                                   ['help', 'ip=', 'port='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ('-i', '--ip'):   ip = arg
        elif opt in ('-p', '--port'): port = arg

    if ip == '' or port == 0:
        print_usage()
        sys.exit()

    return ip, port


def main(arguments):
    log('Start ' + arguments[0])
    ip, port = parse_command_line(arguments[1:])
    log('Start server at %s:%s' % (ip, port))

    thread = Thread(target = listenSerialAndAccumulateData, args = ("COM5", 9600))
    thread.start()
    server = MyTCPServer((ip, int(port)), MyTCPServerHandler)
    server.serve_forever()
    thread.join()


if __name__ == '__main__':
    sys.stdout = open('/var/log/weather_monitor/carrier_proxy_serial.log', 'a')
    sys.stderr = sys.stdout
    main(sys.argv)
