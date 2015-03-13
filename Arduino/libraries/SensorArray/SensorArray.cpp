#include "SensorArray.h"

float readTemper(OneWire sensorPin, byte* addr) {
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  OneWire ds(sensorPin);
  
  if (OneWire::crc8(addr, 7) != addr[7]) {
      return 0;
  }
  // the first ROM byte indicates which chip
  switch (addr[0]) {
    case 0x10:
      type_s = 1;
      break;
    case 0x28:
      type_s = 0;
      break;
    case 0x22:
      type_s = 0;
      break;
    default:
      return 0;
  } 

  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end

  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad

  for (int i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  uint16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) {
      raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    }
    else if (cfg == 0x20) {
      raw = raw & ~3; // 10 bit res, 187.5 ms
    }
    else if (cfg == 0x40) {
      raw = raw & ~1; // 11 bit res, 375 ms
    }
    //// default is 12 bit resolution, 750 ms conversion time
  }
  return (float)raw / 16.0;
}

float readGas(float tempInCels, int analogPin) {
  float condMin = 150;
  float condMax = 200;
  float mgMin = 350;
  float mgMax = 600;
  float gasValue = analogRead(analogPin);

  float coef = 1/(tempInCels * (-0.0208) + 0.9898);
  float gasFinal = coef * gasValue;

  float scale = (mgMax - mgMin)/(condMax - condMin);
  return (mgMin + (gasFinal - condMin) * scale);
}

int readLumin(int pin) {
  int value = analogRead(pin);
  return value;
}