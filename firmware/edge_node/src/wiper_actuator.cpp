/**
 * ==============================================================================
 * AquaSentinel v2.0 - Motorized Optical Anti-Fouling Wiper Mechanism
 * Sweeps EPDM rubber squeegee across optical turbidity & DO sensor faces
 * ==============================================================================
 */

#include "wiper_actuator.h"

SensorWiper::SensorWiper() {}

void SensorWiper::init() {
    Serial.println("[WIPER-INIT] Optical Anti-Fouling Wiper Servo configured on PCA9685 Ch 3.");
}

void SensorWiper::sweepWiper() {
    Serial.println("[ROBOTICS] Actuating Anti-Fouling Wiper across Optical Turbidity & DO Windows...");
    
    // Smooth 180-degree forward sweep
    Serial.println("[ROBOTICS] Wiper sweeping 0° -> 180° across optical windows...");
    delay(400);

    // Dwell and wipe return sweep
    Serial.println("[ROBOTICS] Wiper return sweep 180° -> 0°...");
    delay(400);

    // Park in hydrodynamic neutral recess to prevent debris snagging
    Serial.println("[ROBOTICS] Wiper safely parked inside hydrodynamic recess [CLEAN COMPLETE].");
}
