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
            data = json.loads(self.request.recv(1024).strip())
            # process the data, i.e. print it:
            print data
            # send some 'ok' back
            response = json.dumps(
                [
                    [
                        {'outpost_id': 1},
                        {'time': time.time()},
                        [
                            {'sensor': 1},
                            {'value': 41}
                        ],
                        [
                            {'sensor': 2},
                            {'value': 42}
                        ],
                        [
                            {'sensor': 3},
                            {'value': 43}
                        ],
                        [
                            {'sensor': 4},
                            {'value': 44}
                        ],
                        [
                            {'sensor': 5},
                            {'value': 45}
                        ],
                    ],
                    [
                        {'outpost_id': 2},
                        {'time': time.time()},
                        [
                            {'sensor': 1},
                            {'value': 241}
                        ],
                        [
                            {'sensor': 2},
                            {'value': 242}
                        ],
                        [
                            {'sensor': 3},
                            {'value': 243}
                        ],
                        [
                            {'sensor': 4},
                            {'value': 244}
                        ],
                        [
                            {'sensor': 5},
                            {'value': 245}
                        ]
                    ]
                ]
            )
            print(response)
            self.request.sendall(response)
        except Exception, e:
            print "Exception wile receiving message: ", e


def parse_command_line(arguments):
    ip = ''
    port = 0
    carrier_id = 0
    try:
        opts, args = getopt.getopt(arguments,
                                   'hi:p:c:',
                                   ['help', 'ip=', 'port=', 'carrier_id='])
    except getopt.GetoptError:
        print 'really bad arguments'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'usage message'
            sys.exit()
        elif opt in ('-i', '--ip'):         ip = arg
        elif opt in ('-p', '--port'):       port = arg
        elif opt in ('-c', '--carrier_id'): carrier_id = arg

    return ip, port, carrier_id


def main(arguments):
    ip, port, carrier_id = parse_command_line(arguments)

    server = MyTCPServer((ip, int(port)), MyTCPServerHandler)
    server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
