#TODO add noise: pink, blue, white.
#TODO fuck the thresholds. Apply low pass filter.

import numpy as np
import matplotlib.pyplot as plt

def plot(fig, xlabel, ylabel, x, y, inc):
	if (inc == 1):
		plot.subplot_cntr += 1;
	sp = fig.add_subplot(5, 1, plot.subplot_cntr);
	sp.plot(x, y);
	sp.set_xlabel(xlabel);
	sp.set_ylabel(ylabel);
plot.subplot_cntr = 0;

def filter_spectrum(spectrum, Fs, threshold):
	L = len(spectrum);
	freqs = np.zeros(L / 2);
	amps = np.ones(L / 2);
	k = 0;
	for i in range(0, L / 2):
		if (abs(spectrum[i]) > threshold and i != 0):          #do not touch mean value
			freqs[k] = Fs * i;                      
			amps[k] = 2 * abs(spectrum[i]);
			k = k + 1;
	return freqs, amps;

def restore(amps, freqs, T, t, predict_by):
	tp = T * np.linspace(0, len(t) - 1 + predict_by, L + predict_by);
	y_restored = np.zeros(len(tp));
	for i in range(0, L / 2):
		if freqs[i] == 0:
			break
		y_restored = np.add(y_restored, amps[i] * np.exp(1j * 2 * np.pi * freqs[i]* tp / L));
	return tp, y_restored;

def predict(data, T, Fs, t, predict_by):
	threshold = 0.3;
	Y = np.fft.fft(y) / L;
	F = Fs / 2 * np.linspace(0, 1, L);
	plot(fig1, 'Hz', 'RE(spectrum)', F, np.real(Y), 1);
	plot(fig1, 'Hz', 'IM(spectrum)', F, np.imag(Y), 1);
	freqs, amps = filter_spectrum(Y, Fs, threshold);
	return restore(amps, freqs, T, t, predict_by);

plt.close('all')
fig1 = plt.figure();
L = 1000;
Fs = np.float128(1 / 15.0); #once per 15 secs	
T = np.float128(1 / Fs);				
t = T * np.linspace(0, L - 1, L);
predict_by = Fs * T;	#predict one next value

y = np.sin(2 * np.pi * 37 * t / L) + np.cos(2 * np.pi * 20 * t / L) + np.cos(2 * np.pi * 120 * t / L) + np.cos(2 * np.pi * 111 * t / L);
plot(fig1, 'time(s)', 'signal', t, y, 1);

tp, y_restored = predict(y, T, Fs, t, predict_by);

plot(fig1, 'time(s)', 'RE(restored)', tp, np.real(y_restored), 1);
plot(fig1, 'time(s)', 'RE(restored)', t, np.real(y), 0);
plot(fig1, 'time(s)', 'IM(restored)', tp, np.imag(y_restored), 1);
plot(fig1, 'time(s)', 'IM(restored)', t, np.imag(y), 0);

plt.show();
