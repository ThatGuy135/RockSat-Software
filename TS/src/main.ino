#include <Arduino.h>
#include "Thermocouple_I2C_Control.h"
#include <DualSD.h>
#include <ThreeWayLogger.h>

DualSD DualSDManager;

void setup(){

  Serial.begin(115200);
  LOGGER.begin(&DualSDManager);

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

void createCSVHeader(){
  DualSDManager.initializeFiles("seconds_after_power,hot_junction_1,hot_junction_2,hot_junction_3,hot_junction_4,hot_junction_5,cold_junction_1,cold_junction_2,cold_junction_3,cold_junction_4,cold_junction_5,ADC_1,ADC_2,ADC_3,ADC_4,ADC_5,timed_event_detected_bool");
}

