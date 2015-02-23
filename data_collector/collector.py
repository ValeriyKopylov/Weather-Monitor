#!/usr/bin/env python

import sys
import getopt
import mysql.connector
import socket
import json


def print_usage():
    print """\
Data collector arguments:
./collector.py
    [-u|--user] <DB login>
    [-p|--p] <DB password>
    [-i|--ip] <DB ip address>
    [-n|--name] <DB schema name>
    [-c|--carrier_id] <carrier id in DB>

Example:
./collector.py --user data-collector --password 1 --host_ip 127.0.0.1 --db_name weather_monitor --carrier_id 1
"""


def parse_command_line(arguments):
    user = ''
    password = ''
    host_ip = ''
    db_name = ''
    carrier_id = 0
    try:
        opts, args = getopt.getopt(arguments,
                                   'hu:p:i:n:c:',
                                   ['help', 'user=', 'password=', 'host_ip=', 'db_name=', 'carrier_id='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ('-u', '--user'):       user = arg
        elif opt in ('-p', '--password'):   password = arg
        elif opt in ('-i', '--host_ip'):    host_ip = arg
        elif opt in ('-n', '--db_name'):    db_name = arg
        elif opt in ('-c', '--carrier_id'): carrier_id = arg

    return user, password, host_ip, db_name, carrier_id


def main(arguments):
    user, password, host_ip, db_name, carrier_id = parse_command_line(arguments)

    # Connect to DB
    db_connection = mysql.connector.connect(user=user, password=password, host=host_ip, database=db_name)
    cursor = db_connection.cursor()

    # Get carrier connection parameters
    cursor.execute('SELECT ip, port FROM carrier WHERE carrier_id = %s', carrier_id)
    carrier_ip, carrier_port = cursor.fetchone()

    # Establish connection to carrier
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.connect((carrier_ip, carrier_port))

    # Send request to carrier
    request = {'command': 'GetData'}
    socket_connection.send(json.dumps(request))

    # Receive response from carrier and immediately close socket
    response = socket_connection.recv(1024)
    socket_connection.close()

    # Parse response
    result = json.loads(response)
    for outpost_data in result:
        print outpost_data
        # cursor.execute('INSERT INTO ip, port FROM carrier WHERE carrier_id = %s', carrier_id)

    # Close DB connection
    db_connection.close()


if __name__ == '__main__':
    main(sys.argv[1:])
