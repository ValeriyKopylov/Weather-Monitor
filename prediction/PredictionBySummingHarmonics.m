L = 1000;
t = (0:L-1);

y = exp(1i * 2 * pi * 20 * t / L) + exp(1i * 2 * pi * 120 * t / L) + exp(1i * 2 * pi * 57 * t / L);
sigma1 = 0.7;
sigma2 = 0.9;
noise = [sigma1 * randn(1, L/4) zeros(1, L/2) sigma2 * randn(1, L/4)];
y_unnoised = y;
y = y + noise;
figure(1);
subplot(6,1,1);  
plot(t, real(y));
xlabel('time', 'FontSize', 12);
ylabel('real(s)', 'FontSize', 12);
subplot(6,1,2);  
plot(t, imag(y));
xlabel('time', 'FontSize', 12);
ylabel('imag(s)', 'FontSize', 12);

Y = fft(y) / L;
subplot(6,1,3);  
plot(real(Y));
xlabel('freq', 'FontSize', 12);
ylabel('real(spectrum)', 'FontSize', 12);

subplot(6,1,4);  
plot(imag(Y));
xlabel('freq', 'FontSize', 12);
ylabel('imag(spectrum)', 'FontSize', 12);

threshold = 0.3;

k = 1;
freqs = zeros(1, L/2);
signs = ones(1, L/2);
for i = 1:L/2
    if abs(Y(i)) > threshold && i ~= 1          %do not touch mean value
        freqs(k) = i - 1;                      
        if (Y(i) < 0)
            signs(k) = -1;
        end
        k = k + 1;
    end
end

predict_by = 100;
tp = (0:length(t) + predict_by);
y_restored = zeros(1, length(tp));
for i = 1:L/2
    if freqs(i) == 0
        break
    end
    
    y_restored = y_restored + exp(2 * pi * 1i * freqs(i) * signs(i) * tp / L);
end

subplot(6,1,5);  
plot(tp, real(y_restored), t, real(y_unnoised));
xlabel('time', 'FontSize', 12);
ylabel('restored real', 'FontSize', 12);
subplot(6,1,6);  
plot(tp, imag(y_restored), t, imag(y_unnoised));
xlabel('time', 'FontSize', 12);
ylabel('restored imag', 'FontSize', 12);
