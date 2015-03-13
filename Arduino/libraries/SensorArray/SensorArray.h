typedef unsigned char byte;
#include <stdint.h>
#include <OneWire.h>

float readTemper(OneWire sensorPin, byte* addr);
float readGas(float tempInCels, int analogPin);
int readLumin(int pin);