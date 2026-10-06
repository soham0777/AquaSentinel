/**
 * ==============================================================================
 * AquaSentinel v2.0 - Dual-Track Statistical Event Detection Engine
 * Single Source of Truth implementation matching Appendix B and analytics/detector.py
 * ==============================================================================
 */

#include "anomaly_engine.h"
#include <math.h>

// -----------------------------------------------------------------------------
// RTC Slow Memory Baselines (Survives 15-minute Deep Sleep Cycles)
// -----------------------------------------------------------------------------
RTC_DATA_ATTR static BaselineBin rtc_ph_bins[24];
RTC_DATA_ATTR static BaselineBin rtc_do_bins[24];
RTC_DATA_ATTR static BaselineBin rtc_temp_bins[24];
RTC_DATA_ATTR static BaselineBin rtc_ec_baseline;
RTC_DATA_ATTR static BaselineBin rtc_turb_baseline;

RTC_DATA_ATTR static bool rtc_baselines_initialized = false;
RTC_DATA_ATTR static uint8_t rtc_outlier_history = 0; // Last 3 cycles bitmask
RTC_DATA_ATTR static uint8_t rtc_normal_consecutive = 0;
RTC_DATA_ATTR static RiskLevel rtc_current_risk = RISK_NORMAL;

RTC_DATA_ATTR static SensorReadings rtc_prev_reading;
RTC_DATA_ATTR static bool rtc_has_prev = false;

static const float ALPHA = 1.0f / 96.0f; // Daily EWMA smoothing factor

AnomalyEngine::AnomalyEngine() {}

void AnomalyEngine::init() {
    if (!rtc_baselines_initialized) {
        // Initial cold-boot defaults
        for (int h = 0; h < 24; h++) {
            rtc_ph_bins[h] = { 7.50f, 0.15f };
            rtc_do_bins[h] = { 6.50f, 0.40f };
            rtc_temp_bins[h] = { 24.0f, 1.00f };
        }
        rtc_ec_baseline = { 450.0f, 35.0f };
        rtc_turb_baseline = { 12.0f, 3.0f };
        rtc_baselines_initialized = true;
        rtc_outlier_history = 0;
        rtc_normal_consecutive = 0;
        rtc_current_risk = RISK_NORMAL;
        rtc_has_prev = false;
    }
}

float AnomalyEngine::computeZScore(float val, float mu, float d, float floor_val) {
    float robust_s = 1.4826f * d;
    if (robust_s < floor_val) {
        robust_s = floor_val;
    }
    return fabsf(val - mu) / robust_s;
}

bool AnomalyEngine::checkHardLimits(const SensorReadings& r, AnomalyResult& res) {
    bool tripped = false;
    res.contributing_flags = 0;

    if (r.ph < LIMIT_PH_MIN || r.ph > LIMIT_PH_MAX) {
        tripped = true;
        res.contributing_flags |= (1 << 0);
        snprintf(res.reason, sizeof(res.reason), "HARD_LIMIT: pH=%.2f out of bounds [%.1f, %.1f]", r.ph, LIMIT_PH_MIN, LIMIT_PH_MAX);
    }
    if (r.do_val < LIMIT_DO_MIN) {
        tripped = true;
        res.contributing_flags |= (1 << 2);
        snprintf(res.reason, sizeof(res.reason), "HARD_LIMIT: Hypoxia DO=%.2f mg/L < %.1f mg/L", r.do_val, LIMIT_DO_MIN);
    }
    if (r.ec > LIMIT_EC_MAX) {
        tripped = true;
        res.contributing_flags |= (1 << 1);
        snprintf(res.reason, sizeof(res.reason), "HARD_LIMIT: Saline/Effluent Spike EC=%.1f uS/cm > %.0f uS/cm", r.ec, LIMIT_EC_MAX);
    }
    return tripped;
}

AnomalyResult AnomalyEngine::evaluate(const SensorReadings& r, uint8_t hour_of_day, uint32_t total_cycles) {
    AnomalyResult res;
    res.level = RISK_NORMAL;
    res.max_score = 0.0f;
    res.contributing_flags = 0;
    res.autosampler_trigger = false;
    res.reason[0] = '\0';

    if (hour_of_day >= 24) hour_of_day = 0;

    // 1. Check CPCB Designated Best Use Hard Regulatory Tripwires First
    if (checkHardLimits(r, res)) {
        res.level = RISK_EVENT;
        res.max_score = 99.0f;
        res.autosampler_trigger = true;
        rtc_current_risk = RISK_EVENT;
        rtc_normal_consecutive = 0;
        return res;
    }

    // 2. Compute Robust Diurnal Z-Scores
    float z_ph = computeZScore(r.ph, rtc_ph_bins[hour_of_day].mu, rtc_ph_bins[hour_of_day].d, 0.05f);
    float z_ec = computeZScore(r.ec, rtc_ec_baseline.mu, rtc_ec_baseline.d, 10.0f);
    float z_do = computeZScore(r.do_val, rtc_do_bins[hour_of_day].mu, rtc_do_bins[hour_of_day].d, 0.20f);
    float z_turb = computeZScore(r.turbidity, rtc_turb_baseline.mu, rtc_turb_baseline.d, 2.0f);

    float max_z = z_ph;
    uint8_t flags = 0;

    if (z_ph > 3.0f) { flags |= (1 << 0); }
    if (z_ec > 3.0f) { flags |= (1 << 1); if (z_ec > max_z) max_z = z_ec; }
    if (z_do > 3.0f) { flags |= (1 << 2); if (z_do > max_z) max_z = z_do; }
    if (z_turb > 3.0f) { flags |= (1 << 3); if (z_turb > max_z) max_z = z_turb; }

    res.max_score = max_z;
    res.contributing_flags = flags;

    // 3. Learning Period Bypass (First 7 days = 672 cycles): No statistical events
    if (total_cycles < 672) {
        snprintf(res.reason, sizeof(res.reason), "LEARNING_PERIOD: Baseline learning active (%u/672 cycles)", total_cycles);
        res.level = RISK_NORMAL;
        // Update baselines
        rtc_ph_bins[hour_of_day].mu += ALPHA * (r.ph - rtc_ph_bins[hour_of_day].mu);
        rtc_ph_bins[hour_of_day].d += ALPHA * (fabsf(r.ph - rtc_ph_bins[hour_of_day].mu) - rtc_ph_bins[hour_of_day].d);
        rtc_ec_baseline.mu += ALPHA * (r.ec - rtc_ec_baseline.mu);
        rtc_ec_baseline.d += ALPHA * (fabsf(r.ec - rtc_ec_baseline.mu) - rtc_ec_baseline.d);
        rtc_do_bins[hour_of_day].mu += ALPHA * (r.do_val - rtc_do_bins[hour_of_day].mu);
        rtc_do_bins[hour_of_day].d += ALPHA * (fabsf(r.do_val - rtc_do_bins[hour_of_day].mu) - rtc_do_bins[hour_of_day].d);
        rtc_turb_baseline.mu += ALPHA * (r.turbidity - rtc_turb_baseline.mu);
        rtc_turb_baseline.d += ALPHA * (fabsf(r.turbidity - rtc_turb_baseline.mu) - rtc_turb_baseline.d);
        return res;
    }

    // 4. Persistence Window Logic (Appendix B: >= 2 outliers in last 3 cycles = EVENT)
    bool is_outlier = (flags != 0);
    rtc_outlier_history = ((rtc_outlier_history << 1) | (is_outlier ? 1 : 0)) & 0x07;

    uint8_t outlier_count = 0;
    for (int b = 0; b < 3; b++) {
        if (rtc_outlier_history & (1 << b)) outlier_count++;
    }

    if (outlier_count >= 2) {
        res.level = RISK_EVENT;
        res.autosampler_trigger = (rtc_current_risk != RISK_EVENT); // Trigger once on transition
        rtc_current_risk = RISK_EVENT;
        rtc_normal_consecutive = 0;
        snprintf(res.reason, sizeof(res.reason), "STAT_EVENT: Persistent multi-parameter outlier (Z_max=%.2f, flags=0x%02X)", max_z, flags);
    } else if (outlier_count == 1) {
        res.level = RISK_WATCH;
        rtc_current_risk = RISK_WATCH;
        rtc_normal_consecutive = 0;
        snprintf(res.reason, sizeof(res.reason), "STAT_WATCH: Single-cycle anomaly detected (Z_max=%.2f)", max_z, flags);
    } else {
        // Normal cycle
        rtc_normal_consecutive++;
        if (rtc_normal_consecutive >= 4) {
            rtc_current_risk = RISK_NORMAL; // Clear event after 4 clean cycles
        }
        res.level = rtc_current_risk;
        snprintf(res.reason, sizeof(res.reason), "NORMAL: Water quality within diurnal envelope (Z_max=%.2f)", max_z);

        // Update EWMA baselines ONLY during normal clean conditions
        if (rtc_current_risk == RISK_NORMAL) {
            rtc_ph_bins[hour_of_day].mu += ALPHA * (r.ph - rtc_ph_bins[hour_of_day].mu);
            rtc_ph_bins[hour_of_day].d += ALPHA * (fabsf(r.ph - rtc_ph_bins[hour_of_day].mu) - rtc_ph_bins[hour_of_day].d);
            rtc_ec_baseline.mu += ALPHA * (r.ec - rtc_ec_baseline.mu);
            rtc_ec_baseline.d += ALPHA * (fabsf(r.ec - rtc_ec_baseline.mu) - rtc_ec_baseline.d);
            rtc_do_bins[hour_of_day].mu += ALPHA * (r.do_val - rtc_do_bins[hour_of_day].mu);
            rtc_do_bins[hour_of_day].d += ALPHA * (fabsf(r.do_val - rtc_do_bins[hour_of_day].mu) - rtc_do_bins[hour_of_day].d);
            rtc_turb_baseline.mu += ALPHA * (r.turbidity - rtc_turb_baseline.mu);
            rtc_turb_baseline.d += ALPHA * (fabsf(r.turbidity - rtc_turb_baseline.mu) - rtc_turb_baseline.d);
        }
    }

    rtc_prev_reading = r;
    rtc_has_prev = true;
    return res;
}

void AnomalyEngine::getBaseline(uint8_t param_idx, uint8_t hour, float& out_mu, float& out_scale) {
    if (hour >= 24) hour = 0;
    switch (param_idx) {
        case 0: out_mu = rtc_ph_bins[hour].mu; out_scale = 1.4826f * rtc_ph_bins[hour].d; break;
        case 1: out_mu = rtc_ec_baseline.mu; out_scale = 1.4826f * rtc_ec_baseline.d; break;
        case 2: out_mu = rtc_do_bins[hour].mu; out_scale = 1.4826f * rtc_do_bins[hour].d; break;
        case 3: out_mu = rtc_turb_baseline.mu; out_scale = 1.4826f * rtc_turb_baseline.d; break;
        default: out_mu = 0.0f; out_scale = 1.0f; break;
    }
}
