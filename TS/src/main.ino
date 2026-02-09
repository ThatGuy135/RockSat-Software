#include <Arduino.h>
#include "Thermocouple_I2C_Control.h"
#include <ThreeWayLogger.h>

#define TE_PIN 0

#define SCAN_DELAY 1000

void setup(){

  LOGGER.begin(&DualSDManager);

  int connectedCount = DualSDManager.begin();

  if (connectedCount < 2){
    LOGGER.printf("ONE OR MORE SD CARDS COULD NOT CONNECT!! Number of SD cards connected: %i.\n", connectedCount);
  }

  Serial.println("Serial Established");

  initializeI2C1();

  initializeI2C2();
}

void loop(){
  
  //gather thermocouple data:
  String thermocoupleData = getThermocoupleData();

  //check if TE signal is active:
  int TE = digitalRead(TE_PIN);

  //Save Data:
  double timeInSeconds = millis()/1000.0;
  String combinedCSV = String(timeInSeconds).append(",").append(thermocoupleData).append(TE);
  DualSDManager.writeln(combinedCSV);

  delay(SCAN_DELAY);
}



