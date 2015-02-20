#include <SPI.h>

#include <nRF24L01.h>
#include <RF24.h>
#include <RF24_config.h>

#define CE_PIN   9
#define CSN_PIN 10

const uint64_t pipe = 0xE8E8F0F0E1LL; 
RF24 radio(CE_PIN, CSN_PIN); 

void setup()
{
  Serial.begin(9600);
  radio.begin();
  radio.printDetails();
  radio.setChannel(64);
  radio.openWritingPipe(pipe);
}

void loop()   
{
  char msg[] = "hello world";
  radio.write(msg, sizeof(msg));
}
