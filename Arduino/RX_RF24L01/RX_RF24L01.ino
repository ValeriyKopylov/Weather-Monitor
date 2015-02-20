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
  delay(1000); 
  radio.begin();
  radio.printDetails();
  radio.setChannel(64);
  radio.openReadingPipe(1,pipe);
  radio.startListening();
}

void loop()  
{
  if (radio.available())
  {
    char msg[11];  //hello world - 11 chars
    bool done = false;
    while (!done)
    {
      done = radio.read(msg, sizeof(msg));
    }
    
    for (int i = 0 ; i < 11 ; ++i)
    {
      Serial.print(msg[i]);
    }
    Serial.println();
  }
}
