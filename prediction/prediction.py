#TODO add noise: pink, blue, white.
#TODO take amplitude into account
#TODO fuck the thresholds. Apply low pass filter.

import numpy as np
import matplotlib.pyplot as plt

def plot(fig, xlabel, ylabel, x, y, inc):
	if (inc == 1):
		plot.subplot_cntr += 1;
	sp = fig.add_subplot(6, 1, plot.subplot_cntr);
	sp.plot(x, y);
	sp.set_xlabel(xlabel);
	sp.set_ylabel(ylabel);
plot.subplot_cntr = 0;

plt.close('all')
fig1 = plt.figure();
L = 1000;
t = np.linspace(0, L - 1, L);

y = np.sin(2 * np.pi * 37 * t / L) + np.exp(1j * 2 * np.pi * 20 * t / L) + np.exp(1j * 2 * np.pi * 120 * t / L) + np.exp(1j * 2 * np.pi * 111 * t / L);
plot(fig1, 'time', 'RE(signal)', t, np.real(y), 1);
plot(fig1, 'time', 'IM(signal)', t, np.imag(y), 1);

Y = np.fft.fft(y) / L;
F = np.linspace(0, L - 1, L) / L;
plot(fig1, 'Freq', 'RE(spectrum)', F, np.real(Y), 1);
plot(fig1, 'Freq', 'IM(spectrum)', F, np.imag(Y), 1);

threshold = 0.3;

k = 0;
freqs = np.zeros(L / 2);
signs = np.ones(L / 2);
for i in range(0, L / 2):
    if (abs(Y[i]) > threshold and i != 0):          #do not touch mean value
        freqs[k] = i;                      
        if (Y[i] < 0):
            signs[k] = -1;
        k = k + 1;
        
predict_by = 100;
tp = np.linspace(0, len(t) - 1 + predict_by, L + predict_by);
y_restored = np.zeros(len(tp));
for i in range(0, L / 2):
    if freqs[i] == 0:
        break
    y_restored = np.add(y_restored, np.exp(1j * 2 * np.pi * freqs[i] * signs[i] * tp / L));
 
plot(fig1, 'time', 'RE(restored)', tp, np.real(y_restored), 1);
plot(fig1, 'time', 'RE(restored)', t, np.real(y), 0);
plot(fig1, 'time', 'IM(restored)', tp, np.imag(y_restored), 1);
plot(fig1, 'time', 'IM(restored)', t, np.imag(y), 0);

plt.show();
