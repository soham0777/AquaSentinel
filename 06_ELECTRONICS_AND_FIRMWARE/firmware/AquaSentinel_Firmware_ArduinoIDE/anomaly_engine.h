/**
 * ==============================================================================
 * AquaSentinel v2.0 - Dual-Track Statistical Event Detection Engine
 * Implements Appendix B algorithm: Diurnal EWMA Baselines + CPCB Hard Limits
 * ==============================================================================
 */

#ifndef ANOMALY_ENGINE_H
#define ANOMALY_ENGINE_H

#include <Arduino.h>
#include "config.h"

enum RiskLevel {
    RISK_NORMAL       = 0,
    RISK_WATCH        = 1,
    RISK_EVENT        = 2,
    RISK_SENSOR_FAULT = 3  // a fitted probe gave no valid reading: the station cannot vouch for the water
};

// Per-channel sensor health (bit flags, 0 = good reading). Channel order: pH, EC, DO, turbidity, temperature, stage.
enum SensorHealthCode : uint8_t {
    HEALTH_OK               = 0x00,
    HEALTH_TIMEOUT          = 0x01, // no complete reply
    HEALTH_CRC_ERROR        = 0x02, // bad CRC, or a malformed or foreign reply
    HEALTH_OUT_OF_BOUNDS    = 0x04, // outside the plausible range in config.h
    HEALTH_FLATLINE         = 0x08, // (not detected yet)
    HEALTH_DRIFT_AFTER_WIPE = 0x10, // (not detected yet)
    HEALTH_MODBUS_EXCEPTION = 0x20, // the probe answered with a Modbus exception
    HEALTH_NOT_FITTED       = 0x80  // channel not fitted on this build: not polled, not a fault
};

struct SensorReadings {
    float ph;
    float ec;
    float do_val;
    float turbidity;
    float temperature;
    float stage;
    uint32_t timestamp;
    bool valid[6];     // true only for a fitted channel whose reads all succeeded (value is NaN when none did)
    uint8_t health[6]; // SensorHealthCode bits per channel
};

struct AnomalyResult {
    RiskLevel level;
    float max_score;
    char reason[128];
    uint8_t contributing_flags; // Bitmask: bit0=pH, bit1=EC, bit2=DO, bit3=Turb
    bool autosampler_trigger;
    uint8_t fault_mask;         // channels (health[] order) that are fitted but gave no valid reading
    bool fault_onset;           // true on the cycle a channel newly fails, so the fault alert goes out once
};

// Parameter Baseline Structure (Stored in RTC memory to survive deep sleep)
struct BaselineBin {
    float mu; // EWMA Mean
    float d;  // EWMA Mean Absolute Deviation
};

class AnomalyEngine {
public:
    AnomalyEngine();
    // rtc_state_valid: true after a deep-sleep wake (RTC memory kept). After any other reset the learned
    // baselines and risk state are restored from flash (audit F5). Returns false when there was nothing to
    // restore and the engine starts from the defaults: learning must then start again from cycle 1.
    bool init(bool rtc_state_valid);
    AnomalyResult evaluate(const SensorReadings& r, uint8_t hour_of_day, uint32_t total_cycles);
    void resetBaselines(); // forget learned baselines and history (cold-boot defaults)

    // Flash copy of the learned state: persist() saves it on a risk, fault or learning change, and at
    // least every NVS_SAVE_INTERVAL_CYCLES cycles. Each returns true when flash was read or written.
    bool persist(uint32_t cycle);
    bool saveState();
    bool loadState();

    void getBaseline(uint8_t param_idx, uint8_t hour, float& out_mu, float& out_scale);

private:
    float computeZScore(float val, float mu, float d, float floor_val);
    bool checkHardLimits(const SensorReadings& r, AnomalyResult& res);
    void updateBaselines(const SensorReadings& r, uint8_t hour_of_day);
    void applyFaultOverlay(AnomalyResult& res);
};

#endif // ANOMALY_ENGINE_H
