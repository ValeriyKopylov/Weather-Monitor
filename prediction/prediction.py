import sys
import getopt
import mysql.connector

import matplotlib.pyplot as plt
from spectrum import *
import numpy as np
from scipy import signal
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
./prediction.py --user data-collector --password 1 --host_ip 127.0.0.1 --db_name weather_monitor --sensor_id 1 --date_from "2015-03-01 00:00:00" --date_to "2015-03-01 06:00:00"
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

    # convolve with leaky integrator and apply median filter
    M = 10
    lbd = float(M-1) / float(M)
    h = (1 - lbd) * pow(lbd, np.arange(100))
    x = np.convolve(x, h, 'valid')
    x = signal.medfilt(x, 15)
    # compute regression coefficients.
    while(True):
        global A
        gotException = False
        try:
            [A, E, K] = arburg(x, N)
        except ValueError:
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

    y = zip(*cursor.fetchall())[0]

    plt.close('all')

    # all plots will be there
    fig1 = plt.figure()

    # point where to start prediction
    M = len(y)
    samples_per_half_a_day = 5760 / 2
    # number of samples in extrapolated time series
    P = len(y) + samples_per_half_a_day

    # discretization period
    T = np.float128(15)

    # discretization frequency
    Fs = np.float128(1 / T)


    # time axis of input + predicted samples
    ti = T * np.linspace(0, M - 1, M)

    # input signal
    # secs_in_day = 86400

    # uncomment this while debugging
    # sigma2 = 0.5 #power of the noise
    # noise = sigma2 * np.random.rand(M)
    # noise = 2 * np.random.rand(1, M)[0]
    # s = 10 * np.sin(2*np.pi*50*ti / M)
    # y = y + noise

    # plot noised guy
    plt.plot(ti, y)

    # do the job
    tp, yp = predict(y, P - M, Fs)

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
