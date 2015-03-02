#!/usr/bin/env python

import sys
import getopt
import SocketServer
import json
import time


class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            request = self.request.recv(1024).strip()
            data = json.loads(request)
            # process the data, i.e. print it:
            print ''
            print 'Incoming request from %s:%s' % self.client_address
            print 'Request:  ' + request
            # send some 'ok' back
            response = json.dumps(
                [
                    {
                        'outpost_id': 1,
                        'time': int(time.time()),
                        'T': 41,
                        'P': 42,
                        'H': 43,
                        'L': 44,
                        'G': 45
                    },
                    {
                        'outpost_id': 2,
                        'time': int(time.time()),
                        'T': 141,
                        'P': 142,
                        'H': 143,
                        'L': 144,
                        'G': 145
                    },
                    {
                        'outpost_id': 1,
                        'time': int(time.time()) - 15,
                        'T': 41,
                        'P': 42,
                        'H': 43,
                        'L': 44,
                        'G': 45
                    },
                    {
                        'outpost_id': 2,
                        'time': int(time.time()) - 15,
                        'T': 141,
                        'P': 142,
                        'H': 143,
                        'L': 144,
                        'G': 145
                    },
                ]
            )
            print 'Response: ' + str(response)
            self.request.sendall(response)
        except Exception, e:
            print "Exception wile receiving message: ", e


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
    ip, port = parse_command_line(arguments)
    print 'Start server at %s:%s' % (ip, port)

    server = MyTCPServer((ip, int(port)), MyTCPServerHandler)
    server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
