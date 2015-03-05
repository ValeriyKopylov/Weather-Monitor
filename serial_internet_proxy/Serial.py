#!/usr/bin/env python

import sys
import getopt
import SocketServer
import json
import time
import datetime
import math
import serial


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

            ## todo Accept Com port as an argument
            serial_connection = serial.Serial("COM4", 9600)
            log('Serial connection opened')

            serial_connection.write(request)
            log('Request sent to serial')

            response = serial_connection.read()
            log('Response from serial: ' + response)

            self.request.sendall(response)
            log('Response sent to Ethernet')
        except Exception, e:
            log("Exception wile receiving message: " + str(e))


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

    server = MyTCPServer((ip, int(port)), MyTCPServerHandler)
    server.serve_forever()


if __name__ == '__main__':
    sys.stdout = open('/var/log/weather_monitor/carrier_proxy_serial.log', 'a')
    sys.stderr = sys.stdout
    main(sys.argv)
