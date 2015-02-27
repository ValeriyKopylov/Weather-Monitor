import matplotlib.pyplot as plt
from spectrum import *
import numpy as np
from scipy import signal

plt.close('all')

# point where to start prediction
M = 30000
# number of samples in extrapolated time series1
P = 50000
# order of regression model
N = (P - M) / 10
# all plots will be there
fig1 = plt.figure()
# discretization frequency
Fs = np.float128(1 / 15.0)
# discretization period
T = np.float128(1 / Fs)
# time axis of input + predicted samples
tp = T * np.linspace(0, P - 1, P)
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
x = np.sin(2*np.pi*tp/secs_in_day)\
    + np.sin(2*np.pi*tp/secs_in_month)\
    + np.sin(2*np.pi*tp/secs_in_year)

# generate additive noise
noise = 0.03 * np.random.randn(1, P)
x = x + noise[0]
# plot noised guy
plt.plot(tp[0:P], x)
fig2 = plt.figure()
# design filter using z-transform. we need firwin lowpass filter
filter_denominator = 1
filter_numerator = signal.firwin(N, cutoff=FC, window='hamming')
# apply filter
x = signal.lfilter(filter_numerator, filter_denominator,  x)
# compute regression coefficients.
# TODO handle rho less than 0 exception. Try to predict by smaller interval in the future
[A, E, K] = arburg(x, N)
# allocate memory for output
y = np.zeros(P)
# fill part of the output with known part
y[0:M] = x[0:M]

# apply regression model to the signal.
# actually this is IIR filter.
# use lfilter func in future.
for i in range(M, P):
    y[i] = -1 * np.sum(A * y[i-1:i-1-N:-1])

# plot results
plt.plot(tp, x, tp, y)
# draw current moment
plt.axvline(M * T, -10, 10, linewidth=4, color='r')
# show everything
plt.show()
