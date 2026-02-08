#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MCP9600.h>

Adafruit_MCP9600 mcp;
Adafruit_MCP9600 mcp2;
Adafruit_MCP9600 mcp3;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  Wire1.begin();                 // <-- uses pins 16/17 on Teensy 4.1

  if (!mcp.begin(0x67, &Wire1)) { // <-- tell the library to use Wire1
    Serial.println("MCP9600 not found!");
    while (1) delay(10);
  }

  // Middle of breadboard 0x60
  if (!mcp2.begin(0x60, &Wire1)) { // <-- tell the library to use Wire1
    Serial.println("Middle Thermo Amp not found!");
    while (1) delay(10);
  }

  // At the very end of the breadboard 0x65
  if (!mcp3.begin(0x65, &Wire1)) { // <-- tell the library to use Wire1
    Serial.println("End Thermo Amp not found!");
    while (1) delay(10);
  }

  Serial.println("All Found!");

  mcp.setADCresolution(MCP9600_ADCRESOLUTION_18);
  mcp.setThermocoupleType(MCP9600_TYPE_K);
  mcp2.setADCresolution(MCP9600_ADCRESOLUTION_18);
  mcp2.setThermocoupleType(MCP9600_TYPE_K); // change if not K-type
  mcp3.setADCresolution(MCP9600_ADCRESOLUTION_18);
  mcp3.setThermocoupleType(MCP9600_TYPE_K); // change if not K-type
}

void loop() {
  Serial.print("Hot Junction: ");
  Serial.printf("One: %.2f\n", mcp.readThermocouple());
  Serial.printf("Two: %.2f\n", mcp2.readThermocouple());
  Serial.printf("Three: %.2f\n\n", mcp3.readThermocouple());

  Serial.print("Cold Junction: ");
  Serial.printf("One: %.2f\n", mcp.readAmbient());
  Serial.printf("Two: %.2f\n", mcp2.readAmbient());
  Serial.printf("Three: %.2f\n\n", mcp3.readAmbient());
  Serial.println(" C");

  Serial.print("ADC: ");
  Serial.printf("One: %d\n", mcp.readADC());
  Serial.printf("Two: %d\n", mcp2.readADC());
  Serial.printf("Three: %d\n\n", mcp3.readADC());

  Serial.println("---------------------");
  delay(1000);
}
