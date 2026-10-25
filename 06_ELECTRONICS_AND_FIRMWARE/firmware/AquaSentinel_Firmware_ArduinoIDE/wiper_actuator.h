/**
 * ==============================================================================
 * AquaSentinel v2.0 - Motorized Optical Anti-Fouling Wiper Mechanism
 * Sweeps EPDM rubber squeegee across optical turbidity & DO sensor faces
 * ==============================================================================
 */

#ifndef WIPER_ACTUATOR_H
#define WIPER_ACTUATOR_H

#include <Arduino.h>
#include "config.h"

class SensorWiper {
public:
    SensorWiper();
    void init();
    void sweepWiper();
};

#endif // WIPER_ACTUATOR_H
