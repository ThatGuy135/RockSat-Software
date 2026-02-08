#include <Arduino.h>
#include "Thermocouple_I2C_Control.h"
#include <DualSD.h>

DualSD DualSDManager;

void setup(){

  Serial.begin(115200);

  while (!Serial){
    delay(10);
  }

  Serial.println("Serial Established");

  initializeI2C1();

  initializeI2C2();
}

void loop(){
  printHotJunctions();
  delay(1000);
}


