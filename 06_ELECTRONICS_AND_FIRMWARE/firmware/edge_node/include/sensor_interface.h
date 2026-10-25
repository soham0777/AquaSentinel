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
#include "anomaly_engine.h" // SensorReadings and the SensorHealthCode bits

// Combine repeated reads of one channel (audit F2). The value is the median of the reads that succeeded
// (NaN if none did); the health is the union of every read's error bits, so the channel is valid only when
// all reads succeeded. A fallback value is never marked valid.
void combineReads(const float* values, const uint8_t* codes, uint8_t n, float& out_value, uint8_t& out_health);

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
    uint32_t last_poll_ms;   // end of the previous Modbus transaction (enforces the poll gap)

    uint16_t calculateCRC16(const uint8_t* buffer, uint16_t length);
    // Each returns a SensorHealthCode; on failure the value is NaN, never a stand-in constant
    uint8_t queryModbusRegisters(uint8_t slave_id, uint16_t reg_addr, uint16_t reg_count, uint16_t* dest);

    uint8_t readModbusPH(float& out_ph, float& out_temp);
    uint8_t readModbusEC(float& out_ec);
    uint8_t readModbusDO(float& out_do);
    uint8_t readModbusTurbidity(float& out_turb);
    uint8_t readUltrasonicStage(float& out_stage);
};

#endif // SENSOR_INTERFACE_H
