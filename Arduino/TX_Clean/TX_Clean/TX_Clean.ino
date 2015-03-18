#include <SPI.h>
#include <RF24.h>
#include <OneWire.h>
#include <SensorArray.h>
#include <DHT.h>
#include <movingAvg.h>

#define interval 15

#define RF_CS 9
#define RF_CSN 10
#define DHTPIN 3
#define DHTTYPE DHT11
RF24 radio(RF_CS, RF_CSN);

// Temperature sensor
OneWire ds(2);  // on pin 2 (a 4.7K resistor is necessary)
byte addr[8];


const uint64_t pipes[2] = { 0xe7e7e7e7e7LL, 0xc2c2c2c2c2LL };
static const uint16_t OutpostId = 0x01;
static const uint16_t SensorNumber = 0x06;
static const uint16_t PacketSize = 0x12;
static const byte TempSensorId = 0x01;
static const byte GasSensorId = 0x02;
static const byte HumSensorId = 0x03;
static const byte LightSensorId = 0x04;
static const byte PressSensorId = 0x05;

uint8_t SensorDataBuffer[PacketSize];

DHT dht(DHTPIN, DHTTYPE);

static const int MovingAvgLen = 5;

MovingAvg tempAvg(MovingAvgLen);
MovingAvg gasAvg(MovingAvgLen);
MovingAvg lightAvg(MovingAvgLen);
MovingAvg humAvg(MovingAvgLen);

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.printDetails();
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1, pipes[1]);
  radio.startListening();
  pinMode(DHTPIN, OUTPUT);
  dht.begin();
  // zero sensor data
  memset(SensorDataBuffer, 0, sizeof(SensorDataBuffer) * sizeof(byte));
  
  // fill moving avg buffers
  for (int i = 0 ; i < MovingAvgLen ; ++i)
  {
    float tempC = 0;
    float gasConc = 0;
    float light = 0;
    float humidity = 0;

    for(int i = 1; i < interval + 1; ++i) {
      unsigned long forLoopStart = millis();
      tempC += readTemper(ds, addr);
      gasConc += readGas((tempC / i), A0);
      light += readLumin(A1);
      humidity += dht.readHumidity();
      delay(100);
    }
  
    float midTemp = tempAvg.apply(tempC / interval);
    float midGas = gasAvg.apply(gasConc / interval);
    float midLight = lightAvg.apply(light / interval);
    float midHum = humAvg.apply(humidity / interval);
  }
}

void loop() {
  if (!ds.search(addr)) {
    ds.reset_search();
    return;
  }

  float tempC = 0;
  float gasConc = 0;
  float light = 0;
  float humidity = 0;

  for(int i = 1; i < interval + 1; ++i) {
    unsigned long forLoopStart = millis();
    tempC += readTemper(ds, addr);
    gasConc += readGas((tempC / i), A0);
    light += readLumin(A1);
    humidity += dht.readHumidity();
    delay(1000 - (millis() - forLoopStart));
  }

  float midTemp = tempAvg.apply(tempC / interval);
  float midGas = gasAvg.apply(gasConc / interval);
  float midLight = lightAvg.apply(light / interval);
  float midHum = humAvg.apply(humidity / interval);
  
// TODO: uncomment for demo
  Serial.println(midTemp);
  Serial.println(midGas);
  Serial.println(midLight);
  Serial.println(midHum);

  memset(SensorDataBuffer, 0, sizeof(SensorDataBuffer) * sizeof(byte));
  SensorDataBuffer[0] = OutpostId;
  SensorDataBuffer[1] = OutpostId >> 8;
  writeFloat(midTemp, SensorDataBuffer + sizeof(uint16_t));
  writeFloat(midGas, SensorDataBuffer + sizeof(uint16_t) + sizeof(float)); 
  writeFloat(midLight, SensorDataBuffer + sizeof(uint16_t) + 2 * sizeof(float)); 
  writeFloat(midHum, SensorDataBuffer + sizeof(uint16_t) + 3 * sizeof(float)); 

  // transmit the data
  radio.stopListening();
  radio.write(&SensorDataBuffer, PacketSize);
  radio.startListening();
}

// Most significant byte is last
void writeFloat(const float val, uint8_t* result) {
  uint16_t valIPart = (uint16_t)(val);
  uint16_t valFPart = (uint16_t)((val - valIPart) * 100); // get 2 signs after comma
  uint8_t* valBufferI = (uint8_t*) &valIPart;
  uint8_t* valBufferF = (uint8_t*) &valFPart;
  memcpy(result, valBufferI, sizeof(valBufferI) * sizeof(uint8_t));
  memcpy(result + 2, valBufferF, sizeof(valBufferF) * sizeof(uint8_t));
}
