/**
 * ==============================================================================
 * AquaSentinel v2.0 - Closed-Loop Robotic Autosampler Controller
 * Implements Appendix C logic: 4-Vial Carousel, 20s Purge, NVS Persistence
 * ==============================================================================
 */

#ifndef AUTOSAMPLER_H
#define AUTOSAMPLER_H

#include <Arduino.h>
#include <Preferences.h>
#include "config.h"

struct SampleRecord {
    uint8_t bottle_index; // 0 to 3
    uint32_t cycle;       // decision cycle that took the sample (the clock is not reliable yet, audit F4)
    uint32_t timestamp_utc;
    float ph;
    float ec;
    float do_val;
    float turbidity;
    char reason[64];
    bool collected;
};

class AutoSampler {
public:
    AutoSampler();
    void init();
    
    // Core Appendix C actuation sequence
    bool executeSamplingSequence(const char* reason, uint32_t timestamp_utc, uint32_t cycle,
                                float ph, float ec, float do_val, float turb);

    // True while a new sample must wait: within SAMPLE_LOCKOUT_CYCLES of the last one
    static bool lockoutActive(uint32_t cycle, uint32_t last_sample_cycle);

    uint8_t getFilledBottlesCount();
    bool getSampleRecord(uint8_t bottle_idx, SampleRecord& rec);
    void resetCarouselAfterCollection();

private:
    Preferences prefs;
    uint8_t current_bottle_index;
    uint32_t last_sample_cycle; // 0 = no sample yet

    void setPurgeValve(bool to_waste);
    void runPeristalticPump(uint32_t duration_ms, bool reverse=false);
    bool rotateCarouselToNextBottle();
};

#endif // AUTOSAMPLER_H
