import sys
import getopt
import mysql.connector
import datetime

import matplotlib.pyplot as plt
from spectrum import *
import numpy as np
import time
from scipy import signal
import scipy.cluster.vq as vq
from dateutil.parser import *


def print_usage():
    print """\
Application arguments:
./prediction.py
    [-u|--user] <DB login>
    [-p|--p] <DB password>
    [-i|--ip] <DB ip address>
    [-n|--name] <DB schema name>
    [-s|--sensor_id] <sensor id in DB>
    [-f|--date_from] <prediction start date>
    [-t|--date_to] <prediction end date>

Example:
./prediction.py --user predictor --password 1 --host_ip 127.0.0.1 --db_name weather_monitor --sensor_id 1 --date_from "2015-03-01 00:00:00" --date_to "2015-03-01 06:00:00"
"""


def parse_command_line(arguments):
    user = ''
    password = ''
    host_ip = ''
    db_name = ''
    sensor_id = 0
    date_from = 0
    date_to = 0
    try:
        opts, args = getopt.getopt(
            arguments,
            'hu:p:i:n:s:f:t:',
            ['help', 'user=', 'password=', 'host_ip=', 'db_name=', 'sensor_id=', 'date_from=', 'date_to='])
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
        elif opt in ('-s', '--sensor_id'):
            sensor_id = arg
        elif opt in ('-f', '--date_from'):
            date_from = parse(arg)
        elif opt in ('-t', '--date_to'):
            date_to = parse(arg)

    if user == '' or password == '' or host_ip == '' or db_name == '' or sensor_id == 0 or date_from == 0 or date_to == 0:
        print_usage()
        sys.exit()

    return user, password, host_ip, db_name, sensor_id, date_from, date_to


def predict(x, P, Fs):
    # discretization period
    T = np.float128(1 / Fs)

    # total length of output signal
    L = len(x) + P

    # time axis of input + predicted samples
    tp = T * np.linspace(0, L - 1, L)
    # order of regression model
    N = P

    # convolve with leaky integrator to reduce noise
    #M = 10
    #lbd = float(M-1) / float(M)
    #h = (1 - lbd) * pow(lbd, np.arange(100))
    #x = np.convolve(x, h, 'valid')

    # compute regression coefficients.
    while(True):
        global A
        gotException = False
        try:
            [A, E, K] = arburg(x, N)
        except (ValueError, IndexError):
            gotException = True
            N = N / 2
        if gotException == False:
            break

    # allocate memory for output
    y = np.zeros(L)

    # fill part of the output with known part
    y[0:len(x)] = x

    # apply regression model to the signal.
    # actually this is IIR filter.
    # use lfilter func in future.
    for i in range(len(x), L):
        y[i] = -1 * np.sum(np.real(A) * y[i-1:i-1-N:-1])

    return tp, y


def main(arguments):
    user, password, host_ip, db_name, sensor_id, predict_date_from, predict_date_to = parse_command_line(arguments)

    # Connect to DB
    db_connection = mysql.connector.connect(user=user, password=password, host=host_ip, database=db_name)
    cursor = db_connection.cursor()

    # Get measurements from DB
    base_date_from = predict_date_from - 2 * (predict_date_to - predict_date_from)
    base_date_to = predict_date_from
    cursor.execute("""
        SELECT result
        FROM measurement
        WHERE
            (sensor_id = %s)
            AND
            (change_time BETWEEN %s AND %s)
        ORDER BY change_time
        """, (sensor_id, base_date_from, base_date_to))

    fetched = cursor.fetchall()
    
    t = []
    y = []

    firstUnixTime = time.mktime(fetched[0][0].timetuple())
    for curr_t, curr_y in fetched:
        unixtime = time.mktime(curr_t.timetuple()) - firstUnixTime
        t.append(unixtime)
        y.append(curr_y)

    y = zip(*cursor.fetchall())[0]

    # discretization period
    T = np.float128(15)

    # discretization frequency
    Fs = np.float128(1 / T)

    # point where to start prediction
    M = len(y)
    prediction_length = (predict_date_to - predict_date_from).total_seconds() / T

    # number of samples in extrapolated time series
    P = M + prediction_length
    ti = T * np.linspace(0, M - 1, M)
    if len(t) != len(ti):
        # looks like grid is irregular. Work this out via quantization
        code, dist = vq.vq(ti, t)
        y = y[code]

    # uncomment this while debugging
    # power of the noise
    sigma2 = 0.05
    noise = sigma2 * np.random.rand(M)
    # apply noise
    y += noise

    # plot noised guy
    plt.plot(ti, y)

    # filter the guy first
    y = signal.medfilt(y, 7)

    # do the job
    tp, yp = predict(y, P - M, Fs)

    # filter the output
    y = signal.medfilt(y, 7)

    cursor.execute("""
        DELETE FROM prediction
        WHERE
            (sensor_id = %s)
            AND
            (change_time BETWEEN %s AND %s)
        """, (sensor_id, predict_date_from, predict_date_to))

    prediction_points = []
    curr_t = predict_date_from
    for point in yp[M:]:
        curr_t += datetime.timedelta(seconds=int(T))
        prediction_points.append((sensor_id, curr_t, float(point)))

    cursor.executemany("""
        INSERT INTO prediction (sensor_id, change_time, result)
        VALUES (%s, %s, %s)
        """, prediction_points)

    if True:
        plt.close('all')

        # all plots will be there
        fig1 = plt.figure()

        # plot noised guy
        plt.plot(ti, y)

        # create figure for results
        fig2 = plt.figure()

        # plot results
        plt.plot(ti, y, tp, yp)

        # draw current moment
        plt.axvline(M * T, -10, 10, linewidth=4, color='r')

        # show everything
        plt.show()


if __name__ == '__main__':
    main(sys.argv[1:])
