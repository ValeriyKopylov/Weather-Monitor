import matplotlib.pyplot as plt
from spectrum import *
import numpy as np
from scipy import signal


def predict(x, P, Fs, Fc):
    #discretization period
    T = np.float128(1 / Fs)

    # total length of output signal
    L = len(x) + P

    # time axis of input + predicted samples
    tp = T * np.linspace(0, L - 1, L)

    # order of regression model
    N = P / 10

    # limit regression order
    if (N < 50):
        N = 50
    if (N > 400):
        N = 400

    # design filter using z-transform. we need firwin lowpass filter
    A = 1
    B = signal.firwin(50, cutoff=Fc, window='hamming')

    # apply filter
    x = signal.lfilter(B, A, x)

    # compute regression coefficients.
    # TODO handle rho less than 0 exception. Try to predict by smaller interval in the future
    [A, E, K] = arburg(x, N)

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

plt.close('all')

# all plots will be there
fig1 = plt.figure()

# point where to start prediction
M = 3000
# number of samples in extrapolated time series1
P = 5000

# discretization frequency
Fs = np.float128(1 / 15.0)

# discretization period
T = np.float128(1 / Fs)

# time axis of input + predicted samples
ti = T * np.linspace(0, M - 1, M)

# input signal
secs_in_day = 86400
secs_in_month = 86400 * 30
secs_in_year = secs_in_month * 12

# signal at 1/15/86400 HZ
# + signal at 1/15/86400/30 HZ
# + signal at 1/15/86400/30/12 HZ
# So cutoff can be 1/15/86400 will be ok
# Cut off frequency for firwin filter
FC = Fs / secs_in_day #Hz

# signal itself
x = np.sin(2*np.pi*ti/secs_in_day)\
    + np.sin(2*np.pi*ti/secs_in_month)\
    + np.sin(2*np.pi*ti/secs_in_year)

# generate additive noise
noise = 0.03 * np.random.randn(1, M)
x = x + noise[0]
# plot noised guy
plt.plot(ti, x)

# create figure for results
fig2 = plt.figure()
# do the job
tp, y = predict(x, P - M, Fs, FC)

# compare with continued signal
# TODO remove this during integration with db
x = np.sin(2*np.pi*tp/secs_in_day)\
    + np.sin(2*np.pi*tp/secs_in_month)\
    + np.sin(2*np.pi*tp/secs_in_year)

# plot results
plt.plot(tp, x, tp, y)
# draw current moment
plt.axvline(M * T, -10, 10, linewidth=4, color='r')
# show everything
plt.show()
