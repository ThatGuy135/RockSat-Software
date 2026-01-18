#ifndef THREEWAYLOGGER_H
#define THREEWAYLOGGER_H

#include <Arduino.h>
#include <DualSD.h>
#include "defines.h"

/// @brief A utility to log to serial, a debug file, and the external UART in one call.
class ThreeWayLogger 
{
public:
    DualSD* dualSd;

    void printf(const String& s, ...);
    void print(const String &s);
    void println(const String &s);
    void println(const Printable &p);
    void print(const Printable &p);
    void begin(DualSD* dual);
};


extern ThreeWayLogger LOGGER;

#endif