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
    RISK_NORMAL = 0,
    RISK_WATCH  = 1,
    RISK_EVENT  = 2
};

struct SensorReadings {
    float ph;
    float ec;
    float do_val;
    float turbidity;
    float temperature;
    float stage;
    uint32_t timestamp;
    bool valid[6]; // Flags indicating sensor health
};

struct AnomalyResult {
    RiskLevel level;
    float max_score;
    char reason[128];
    uint8_t contributing_flags; // Bitmask: bit0=pH, bit1=EC, bit2=DO, bit3=Turb
    bool autosampler_trigger;
};

// Parameter Baseline Structure (Stored in RTC memory to survive deep sleep)
struct BaselineBin {
    float mu; // EWMA Mean
    float d;  // EWMA Mean Absolute Deviation
};

class AnomalyEngine {
public:
    AnomalyEngine();
    void init();
    AnomalyResult evaluate(const SensorReadings& r, uint8_t hour_of_day, uint32_t total_cycles);

    void getBaseline(uint8_t param_idx, uint8_t hour, float& out_mu, float& out_scale);

private:
    float computeZScore(float val, float mu, float d, float floor_val);
    bool checkHardLimits(const SensorReadings& r, AnomalyResult& res);
};

#endif // ANOMALY_ENGINE_H
