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
#include <esp_system.h>
#include <Preferences.h>
#include "config.h"
#include "sensor_interface.h"
#include "anomaly_engine.h"
#include "autosampler.h"
#include "wiper_actuator.h"
#include "microsd_logger.h"
#include "telemetry_comm.h"

#ifndef PIO_UNIT_TESTING // unit tests (pio test) bring their own setup() and loop()

SensorManager sensorMgr;
AnomalyEngine anomalyEngine;
AutoSampler autoSampler;
SensorWiper sensorWiper;
MicroSDLogger sdLogger;
TelemetryManager telemetryMgr;

// Decision cycle counter, kept in flash (audit F5). Learning progress, the sampler lockout, the wiper and the
// upload cadence all count cycles; the RTC boot counter this replaces restarted at 0 after every power cut.
static uint32_t nextCycle(bool restart) {
    Preferences prefs;
    if (!prefs.begin(NODE_NVS_NAMESPACE, false)) {
        Serial.println("[NVS-ERROR] Cycle counter unavailable: counting this as cycle 1");
        return 1;
    }
    uint32_t cycle = restart ? 1 : prefs.getUInt("cycle", 0) + 1;
    prefs.putUInt("cycle", cycle);
    prefs.end();
    return cycle;
}

static const char* resetReasonName(esp_reset_reason_t reason) {
    switch (reason) {
        case ESP_RST_POWERON:   return "power-on";
        case ESP_RST_EXT:       return "external pin";
        case ESP_RST_SW:        return "software restart";
        case ESP_RST_PANIC:     return "crash";
        case ESP_RST_INT_WDT:
        case ESP_RST_TASK_WDT:
        case ESP_RST_WDT:       return "watchdog";
        case ESP_RST_DEEPSLEEP: return "deep-sleep wake";
        case ESP_RST_BROWNOUT:  return "brown-out";
        default:                return "other";
    }
}

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
        case RISK_SENSOR_FAULT:
            Serial.println("[BEACON-JALDEEP] Visual Beacon -> BLINKING WHITE (SENSOR FAULT: readings cannot be trusted, check the probes)");
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(200);

    // A deep-sleep wake keeps RTC memory. Any other reset (power cut, brown-out, watchdog, crash) clears it,
    // so the engine restores its learned state from flash instead (audit F5)
    esp_reset_reason_t reset_reason = esp_reset_reason();
    bool state_restored = anomalyEngine.init(reset_reason == ESP_RST_DEEPSLEEP);
    uint32_t cycle = nextCycle(!state_restored); // nothing to restore: learning starts again at cycle 1

    Serial.println("\n=================================================================");
    Serial.println(" AQUASENTINEL v2.0 - ROBOTICS WATER QUALITY SENTINEL");
    Serial.println(" Team: Sanjivani Hero's Journey | Sanjivani University, Kopargaon");
    Serial.printf(" Decision Cycle: #%lu | Reset: %s | Learned State: %s\n", (unsigned long)cycle,
                  resetReasonName(reset_reason), state_restored ? "kept" : "defaults (learning restarts)");
    Serial.println("=================================================================");

    // 1. Initialize Subsystems
    autoSampler.init();
    sensorWiper.init();
    sensorMgr.init();
    sdLogger.init();
    telemetryMgr.init();

    // 2. Wiper Maintenance Routine (Every 6 Hours = 24 Cycles)
    if (cycle % WIPER_INTERVAL_CYCLES == 0) {
        sensorWiper.sweepWiper();
    }

    // 3. SENSE: Power on sensor rail, stabilize, and acquire 3-sample median
    sensorMgr.powerOnSensors();
    SensorReadings readings = sensorMgr.acquireReadings();
    sensorMgr.powerOffSensors();

    Serial.printf("[ACQUIRE] pH=%.2f | EC=%.1f uS/cm | DO=%.2f mg/L | Turb=%.1f NTU | Temp=%.1f C | Stage=%.2f m\n",
                  readings.ph, readings.ec, readings.do_val, readings.turbidity, readings.temperature, readings.stage);

    // 4. DECIDE: Evaluate Multivariate Statistical Anomaly Engine
    uint8_t hour_of_day = (readings.timestamp / 3600) % 24;
    AnomalyResult anomaly = anomalyEngine.evaluate(readings, hour_of_day, cycle);

    Serial.printf("[DECIDE] Risk Level: %d | Max Z-Score: %.2f | Status: %s\n",
                  anomaly.level, anomaly.max_score, anomaly.reason);

    // 5. ACT: Visual Beacon Riverbank Status
    setVisualBeacon(anomaly.level);

    // 6. ACT: Robotics Autosampler Trigger
    if (anomaly.autosampler_trigger) {
        autoSampler.executeSamplingSequence(anomaly.reason, readings.timestamp, cycle,
                                           readings.ph, readings.ec, readings.do_val, readings.turbidity);
    }

    // Save the decision state after the sample: a power cut mid-sample lets the next cycle retry it, and the
    // cycle lockout stops a repeat once the bottle is sealed (audit F5, F7)
    anomalyEngine.persist(cycle);

    // 7. ACT: MicroSD Atomic Persistence & 4G LTE Telemetry
    sdLogger.logReading(readings, anomaly);

    // Upload immediately on EVENT or a new sensor fault, otherwise hourly batch (every 4 cycles)
    if (anomaly.level == RISK_EVENT || anomaly.fault_onset || (cycle % 4 == 0)) {
        String frame = telemetryMgr.serializePayload(readings, anomaly, cycle,
                                                     autoSampler.getFilledBottlesCount());
        telemetryMgr.transmit(frame, anomaly.level == RISK_EVENT);
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

#endif // PIO_UNIT_TESTING
