#!/usr/bin/env python

import sys
import getopt
import mysql.connector
import socket
import json
import time
import datetime
import textwrap


def log(message):
    print '[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), message)
    sys.stdout.flush()


def execute_sql(cursor, query, args):
    cursor.execute(query, args)
    log(textwrap.dedent(cursor._executed).strip('\n').replace('\n', ' '))


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
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-p', '--password'):
            password = arg
        elif opt in ('-i', '--host_ip'):
            host_ip = arg
        elif opt in ('-n', '--db_name'):
            db_name = arg
        elif opt in ('-c', '--carrier_id'):
            carrier_id = int(arg)

    if user == '' or password == '' or host_ip == '' or db_name == '' or carrier_id == 0:
        print_usage()
        sys.exit()

    return user, password, host_ip, db_name, carrier_id


def parse_outpost_data(outpost_data):
    outpost_id = 0
    change_time = 0
    measurements = {}
    for key in outpost_data:
        if key == 'outpost_id':
            outpost_id = outpost_data[key]
        elif key == 'time':
            change_time = outpost_data[key]
        else:
            measurements[key] = outpost_data[key]

    return outpost_id, change_time, measurements


def main(arguments):
    start_message = 'Start'
    for arg in arguments:
        start_message += ' ' + str(arg)
    log(start_message)

    user, password, host_ip, db_name, carrier_id = parse_command_line(arguments[1:])

    # Connect to DB
    db_connection = mysql.connector.connect(user=user, password=password, host=host_ip, database=db_name)
    cursor = db_connection.cursor()

    # Get carrier connection parameters
    execute_sql(cursor, 'SELECT ip, port FROM carrier WHERE carrier_id = %s', (carrier_id,))
    carrier_ip, carrier_port = cursor.fetchone()

    # Establish connection to carrier
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.connect((carrier_ip, carrier_port))
    log('Connect to carrier at ' + carrier_ip + ':' + str(carrier_port))

    # Send request to carrier
    json_request = {"command": "GetData", "time": int(time.time())}
    raw_request = json.dumps(json_request, encoding='ascii')
    log('Request to carrier: "' + raw_request + '"')
    socket_connection.send(raw_request)

    # Receive response from carrier and immediately close socket
    raw_response = socket_connection.recv(1024)
    socket_connection.close()
    response_time = time.localtime()
    log('Response from carrier: "' + raw_response + '"')

    # Update last contact time for the carrier
    execute_sql(cursor, 'UPDATE carrier SET last_contact_time = %s WHERE carrier_id = %s', (response_time, carrier_id))

    # Parse response
    json_response = json.loads(raw_response)
    connected_outposts = []
    for outpost_data in json_response:
        outpost_id, change_time, measurements = parse_outpost_data(outpost_data)
        if outpost_id == 0 or change_time == 0:
            continue
        for sensor_type, measurement_result in measurements.items():
            execute_sql(cursor, """
                SELECT sensor.sensor_id FROM sensor
                LEFT JOIN sensor_type USING(sensor_type_id)
                WHERE sensor.outpost_id = %s AND sensor_type.short_name = %s
                """, (outpost_id, sensor_type))
            sensor_id = cursor.fetchone()[0]
            execute_sql(cursor, """
                INSERT INTO measurement (carrier_id, sensor_id, change_time, result)
                VALUES (%s, %s, %s, %s)
                """, (carrier_id, sensor_id, datetime.datetime.fromtimestamp(change_time), measurement_result))

        # Update outpost connection info
        if outpost_id not in connected_outposts:
            connected_outposts.append(outpost_id)
            execute_sql(cursor, """
                UPDATE outpost
                SET last_contact_time = %s, last_carrier_id = %s
                WHERE outpost_id = %s
                """, (response_time, carrier_id, outpost_id))

    # Close DB connection
    db_connection.commit()
    db_connection.close()
    log('Measurements have been committed to DB')


if __name__ == '__main__':
    sys.stdout = open('/var/log/weather_monitor/data_collector.log', 'a')
    sys.stderr = sys.stdout
    main(sys.argv)
