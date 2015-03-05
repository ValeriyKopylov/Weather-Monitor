#include <SPI.h>
#include <RF24.h>

#define RF_CS 9
#define RF_CSN 10
RF24 radio(RF_CS, RF_CSN);
const uint64_t pipes[2] = { 0xe7e7e7e7e7LL, 0xc2c2c2c2c2LL };

static const uint16_t OutpostId = 0x01;
static const uint16_t SensorNumber = 0x06;
static const uint16_t PacketSize = 0x12;
static const byte TempSensorId = 0x01;
static const byte GasSensorId = 0x02;
static const byte HumSensorId = 0x03;
static const byte LightSensorId = 0x04;
static const byte PressSensorId = 0x05;

float temperature;
float gas;
float humidity;
float light;
float pressure;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.printDetails();
  radio.openWritingPipe(pipes[1]); // note that our pipes are the same above, but that
  radio.openReadingPipe(1, pipes[0]); // they are flipped between rx and tx sides.
  radio.startListening();
}

void loop() {
  if (radio.available()) {
    byte rx_data[PacketSize];
    bool done = false;
    while (!done) {
      done = radio.read(&rx_data, PacketSize);
    }
    Serial.write(rx_data, PacketSize);
  }
}
