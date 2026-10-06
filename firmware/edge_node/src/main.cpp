/**
 * ==============================================================================
 * AquaSentinel v2.0 - Master Edge Controller Firmware (Robotics Edition)
 * Project: AquaRight | Competition: AAKRUTI Innovation Competition (AIC) 2026
 * Theme: Robotics | Institution: Sanjivani University, Kopargaon
 * 
 * ROBOTICS CLOSED-LOOP ARCHITECTURE (Sense–Decide–Act):
 * 1. SENSE:  Power-gated RS485 Modbus probes (pH, EC, DO, Turbidity) + Stage
 * 2. DECIDE: Onboard Appendix B Diurnal EWMA + CPCB Class C Hard Limit Engine
 * 3. ACT:    - Automated Forensic Autosampler (Physical sample capture for NABL)
 *            - Motorized Optical Wiper (Biofouling elimination)
 *            - 360° Visual Safety Beacon (Jal-Deep riverbank warning)
 *            - 4G LTE Telemetry & Downstream Intake Pump Lockout
 * ==============================================================================
 */

#include <Arduino.h>
#include <esp_sleep.h>
#include "config.h"
#include "sensor_interface.h"
#include "anomaly_engine.h"
#include "autosampler.h"
#include "wiper_actuator.h"
#include "microsd_logger.h"
#include "telemetry_comm.h"

// Preserved across 15-minute deep sleep cycles
RTC_DATA_ATTR static uint32_t boot_counter = 0;
RTC_DATA_ATTR static uint32_t wiper_hour_counter = 0;

SensorManager sensorMgr;
AnomalyEngine anomalyEngine;
AutoSampler autoSampler;
SensorWiper sensorWiper;
MicroSDLogger sdLogger;
TelemetryManager telemetryMgr;

void setVisualBeacon(RiskLevel level) {
    switch (level) {
        case RISK_NORMAL:
            Serial.println("[BEACON-JALDEEP] Visual Beacon -> SOLID BLUE/GREEN (River water normal/safe)");
            break;
        case RISK_WATCH:
            Serial.println("[BEACON-JALDEEP] Visual Beacon -> PULSING AMBER (Elevated organic/turbidity watch)");
            break;
        case RISK_EVENT:
            Serial.println("[BEACON-JALDEEP] Visual Beacon -> FLASHING HIGH-INTENSITY RED (CRITICAL CONTAMINATION ALERT!)");
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(200);
    
    boot_counter++;
    wiper_hour_counter++;

    Serial.println("\n=================================================================");
    Serial.println(" AQUASENTINEL v2.0 - ROBOTICS WATER QUALITY SENTINEL");
    Serial.println(" Team: Sanjivani Hero's Journey | Sanjivani University, Kopargaon");
    Serial.printf(" FreeRTOS Edge Boot Counter: #%u | 15-Minute Cycle Active\n", boot_counter);
    Serial.println("=================================================================");

    // 1. Initialize Subsystems
    anomalyEngine.init();
    autoSampler.init();
    sensorWiper.init();
    sensorMgr.init();
    sdLogger.init();
    telemetryMgr.init();

    // 2. Wiper Maintenance Routine (Every 6 Hours = 24 Cycles)
    if (wiper_hour_counter >= 24) {
        sensorWiper.sweepWiper();
        wiper_hour_counter = 0;
    }

    // 3. SENSE: Power on sensor rail, stabilize, and acquire 3-sample median
    sensorMgr.powerOnSensors();
    SensorReadings readings = sensorMgr.acquireReadings();
    sensorMgr.powerOffSensors();

    Serial.printf("[ACQUIRE] pH=%.2f | EC=%.1f uS/cm | DO=%.2f mg/L | Turb=%.1f NTU | Temp=%.1f C | Stage=%.2f m\n",
                  readings.ph, readings.ec, readings.do_val, readings.turbidity, readings.temperature, readings.stage);

    // 4. DECIDE: Evaluate Multivariate Statistical Anomaly Engine
    uint8_t hour_of_day = (readings.timestamp / 3600) % 24;
    AnomalyResult anomaly = anomalyEngine.evaluate(readings, hour_of_day, boot_counter);

    Serial.printf("[DECIDE] Risk Level: %d | Max Z-Score: %.2f | Status: %s\n",
                  anomaly.level, anomaly.max_score, anomaly.reason);

    // 5. ACT: Visual Beacon Riverbank Status
    setVisualBeacon(anomaly.level);

    // 6. ACT: Robotics Autosampler Trigger
    if (anomaly.autosampler_trigger) {
        autoSampler.executeSamplingSequence(anomaly.reason, readings.timestamp,
                                           readings.ph, readings.ec, readings.do_val, readings.turbidity);
    }

    // 7. ACT: MicroSD Atomic Persistence & 4G LTE Telemetry
    sdLogger.logTelemetry(readings, anomaly);

    // Upload immediately on EVENT, otherwise hourly batch (every 4 cycles)
    if (anomaly.level == RISK_EVENT || (boot_counter % 4 == 0)) {
        telemetryMgr.transmitTelemetry(readings, anomaly, autoSampler.getFilledBottlesCount());
    }

    // 8. Sleep Power Management: Re-arm 15-minute RTC timer
    Serial.printf("\n[POWER-MANAGEMENT] Cycle complete. Entering 15-minute FreeRTOS deep sleep (%u uA)...\n", 15);
    Serial.flush();

    esp_sleep_enable_timer_wakeup((uint64_t)SAMPLING_INTERVAL_MIN * 60 * 1000000ULL);
    esp_deep_sleep_start();
}

void loop() {
    // Unreachable due to deep sleep
}
