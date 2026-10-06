/**
 * ==============================================================================
 * AquaSentinel v2.0 - Industrial RS485 Modbus-RTU Multi-Sensor Interface
 * Supports DFRobot SEN0708 (pH), SEN0707 (EC), SEN0680 (DO), SEN0710 (Turbidity)
 * and Ultrasonic Stage Measurement with CRC16, 3-sample median, and health flags.
 * ==============================================================================
 */

#ifndef SENSOR_INTERFACE_H
#define SENSOR_INTERFACE_H

#include <Arduino.h>
#include "config.h"
#include "anomaly_engine.h"

enum SensorHealthCode {
    HEALTH_OK               = 0x00,
    HEALTH_TIMEOUT          = 0x01,
    HEALTH_CRC_ERROR        = 0x02,
    HEALTH_OUT_OF_BOUNDS    = 0x04,
    HEALTH_FLATLINE         = 0x08,
    HEALTH_DRIFT_AFTER_WIPE = 0x10
};

class SensorManager {
public:
    SensorManager();
    void init();
    void powerOnSensors();
    void powerOffSensors();
    
    // Core sampling method
    SensorReadings acquireReadings();

    uint8_t getHealthStatus(uint8_t sensor_idx) const { return health_flags[sensor_idx]; }

private:
    uint8_t health_flags[6]; // pH, EC, DO, Turbidity, Temp, Stage

    uint16_t calculateCRC16(const uint8_t* buffer, uint16_t length);
    bool queryModbusRegisters(uint8_t slave_id, uint16_t reg_addr, uint16_t reg_count, uint16_t* dest);
    
    float readModbusPH(float& out_temp);
    float readModbusEC();
    float readModbusDO();
    float readModbusTurbidity();
    float readUltrasonicStage();
    float computeMedian(float a, float b, float c);
};

#endif // SENSOR_INTERFACE_H
