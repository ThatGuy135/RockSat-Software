#include "main.h"
#include "defines.h"
#include "sensors/IMU.h"
#include "sensors/Pressure.h"

/// If the serial did not connect.
bool faultySerial = false;
/// If the IMU did not connect.
bool faultyIMU = false;

/// The IMU connection.
IMU imu;
Pressure pressure = Pressure();

void setup()
{
    // Setup serial.
    if (setup_serial()) 
    {
        // Should be connected.
        SerialUSB.println("Connected to the serial.");
    }
    
    if (pressure.connect_to_sensor()) 
    {
        SerialUSB.println("Pressure sensor connected!");
        pressure.configure_sensor();
    }
    else
    {
        SerialUSB.println("Pressure not connected. Moving on without pressure :(");
    }
    
    //Setup the IMU.
    if (imu.connect_to_imu())
    {
        SerialUSB.println("IMU connected!!");
        imu.configure_imu();
    }
    else
    {
        SerialUSB.println("IMU not connected. Moving on without IMU :(");
    }
}

void loop() 
{
    imu.imu_loop();
    pressure.sensor_loop();
    delay(LOOP_DELAY);
}


/// Start the serial connection.
/// @return True if connected.
bool setup_serial() 
{
    // Try to connect to USB Serial.
    SerialUSB.begin(BAUD_RATE_RSX);
    
    // Prevent an infinate loop by setting an upper bound.
    int safetyCount = 0;
    while (!SerialUSB && safetyCount < RETRY_MAX) 
    {
        delay(10);
        safetyCount++;
    }
    
    faultySerial = safetyCount >= RETRY_MAX;
    return !faultySerial;
}
