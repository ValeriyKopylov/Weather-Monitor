#!/usr/bin/env python

import sys
import getopt
import SocketServer
import json
import time
import datetime
import math


def log(message):
    print '[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), message)
    sys.stdout.flush()

def scale(value, actual_min, actual_max, required_min, required_max):
    return (1.0 * value - actual_min) * (required_max - required_min) / (actual_max - actual_min) + required_min


class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            log('Incoming request from %s:%s' % self.client_address)
            request = self.request.recv(1024).strip()
            data = json.loads(request)
            log('Request:  ' + request)

            t_curr = datetime.datetime.now()
            t_start_year = datetime.datetime(t_curr.year, 1, 1, 0, 0, 0)
            t_start_day = datetime.datetime(t_curr.year, t_curr.month, t_curr.day, 0, 0, 0)
            t_fraction_of_year = 2 * math.pi * (t_curr - t_start_year).total_seconds() / (3600 * 24 * 365)
            t_fraction_of_day = 2 * math.pi * (t_curr - t_start_day).total_seconds() / (3600 * 24)

            value = (-1.0 * math.cos(t_fraction_of_year) - math.cos(t_fraction_of_day) / 5.0) / (1 + 1 / 5.0)
            response = json.dumps(
                [
                    {
                        'outpost_id': 1,
                        'time': int(time.time()),
                        'T': scale(value, -1, 1, -30, 40),
                        'P': scale(value, -1, 1, 720, 770),
                        'H': scale(value, -1, 1, 0, 100),
                        'L': scale(value, -1, 1, 0, 20000),
                        'G': scale(value, -1, 1, 0.00035, 0.00045),
                    },
                    {
                        'outpost_id': 2,
                        'time': int(time.time()),
                        'T': scale(value, -1, 1, -30, 40),
                        'P': scale(value, -1, 1, 720, 770),
                        'H': scale(value, -1, 1, 0, 100),
                        'L': scale(value, -1, 1, 0, 20000),
                        'G': scale(value, -1, 1, 0.00035, 0.00045),
                    },
                ]
            )
            log('Response: ' + str(response))
            self.request.sendall(response)
        except Exception, e:
            log("Exception wile receiving message: " + str(e))


def print_usage():
    print """\
Carrier Emulator arguments:
./carrier_emulator.py [-i|--ip] <ip address> [-p|--port] <port>

Example:
./carrier_emulator.py --ip 127.0.0.1 --port 4242
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
    start_message = 'Start'
    for arg in arguments:
        start_message += ' ' + str(arg)
    log(start_message)

    ip, port = parse_command_line(arguments[1:])
    log('Start server at %s:%s' % (ip, port))

    server = MyTCPServer((ip, int(port)), MyTCPServerHandler)
    server.serve_forever()


if __name__ == '__main__':
    sys.stdout = open('/var/log/weather_monitor/carrier_emulator.log', 'a')
    sys.stderr = sys.stdout
    main(sys.argv)
