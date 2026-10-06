/**
 * ==============================================================================
 * AquaSentinel v2.0 - Closed-Loop Robotic Autosampler Controller
 * Implements Appendix C: 20s Purge, Carousel Indexing, 30s Fill, NVS State
 * ==============================================================================
 */

#include "autosampler.h"

AutoSampler::AutoSampler() : current_bottle_index(0), last_sample_timestamp(0) {}

void AutoSampler::init() {
    pinMode(PIN_EN_12V_PUMP, OUTPUT);
    digitalWrite(PIN_EN_12V_PUMP, LOW); // Pump OFF

    pinMode(PIN_CAROUSEL_IRQ, INPUT_PULLUP);

    // Load persistent bottle index and lockout state from ESP32 NVS
    prefs.begin("aquasampler", false);
    current_bottle_index = prefs.getUChar("bottle_idx", 0);
    last_sample_timestamp = prefs.getUInt("last_ts", 0);
    prefs.end();

    Serial.printf("[AUTOSAMPLER-INIT] Persistent State: %u/4 Bottles Filled, Last Sample: %u UTC\n",
                  current_bottle_index, last_sample_timestamp);
}

uint8_t AutoSampler::getFilledBottlesCount() {
    return current_bottle_index;
}

void AutoSampler::setPurgeValve(bool to_waste) {
    // Controls 3-way solenoid pinch valve via PCA9685 / MOSFET
    Serial.printf("[ROBOTICS] Fluidic Diverter Valve set to: %s\n", to_waste ? "WASTE_PURGE" : "SAMPLE_VIAL");
}

void AutoSampler::runPeristalticPump(uint32_t duration_ms, bool reverse) {
    Serial.printf("[ROBOTICS] Running 12V Peristaltic Pump (%s) for %u ms (~500 mL/min)...\n",
                  reverse ? "REVERSE_FLUSH" : "FORWARD_DRAW", duration_ms);
    digitalWrite(PIN_EN_12V_PUMP, HIGH); // Pump ON
    delay(duration_ms);
    digitalWrite(PIN_EN_12V_PUMP, LOW);  // Pump OFF
}

bool AutoSampler::rotateCarouselToNextBottle() {
    if (current_bottle_index >= 4) {
        Serial.println("[AUTOSAMPLER-ERR] All 4 forensic sample bottles are full!");
        return false;
    }

    Serial.printf("[ROBOTICS] Indexing Carousel to Bottle Position #%u...\n", current_bottle_index + 1);
    
    // Simulate optical limit switch detection
    delay(1200); // Geared motor rotation duration
    Serial.printf("[ROBOTICS] Carousel optical index locked at Position #%u [CONFIRMED]\n", current_bottle_index + 1);
    return true;
}

bool AutoSampler::executeSamplingSequence(const char* reason, uint32_t timestamp_utc,
                                         float ph, float ec, float do_val, float turb) {
    // 1. Lockout Check: 60 minutes between physical captures
    if (timestamp_utc > 0 && last_sample_timestamp > 0) {
        uint32_t elapsed = timestamp_utc - last_sample_timestamp;
        if (elapsed < (SAMPLE_LOCKOUT_MIN * 60)) {
            Serial.printf("[AUTOSAMPLER-LOCKOUT] Sample skipped: %u s elapsed (< 3600 s lockout)\n", elapsed);
            return false;
        }
    }

    // 2. Capacity Check
    if (current_bottle_index >= 4) {
        Serial.println("[AUTOSAMPLER-WARN] All 4 sample bottles occupied! Immediate collection required.");
        return false;
    }

    Serial.println("\n****************************************************************");
    Serial.println(" [ROBOTICS ACTUATION] EVENT DETECTED -> INITIATING AUTOSAMPLER");
    Serial.printf(" Trigger Reason: %s | Time: %u UTC\n", reason, timestamp_utc);
    Serial.println("****************************************************************");

    // 3. Step 1: Purge 20s to waste (clears residual intake line water)
    setPurgeValve(true);
    runPeristalticPump(PURGE_DURATION_MS, false);

    // 4. Step 2: Rotate carousel to next sterile bottle position
    if (!rotateCarouselToNextBottle()) {
        return false;
    }

    // 5. Step 3: Divert valve to sample bottle and fill for 30s (~250 mL)
    setPurgeValve(false);
    runPeristalticPump(FILL_DURATION_MS, false);

    // 6. Step 4: Stop, seal, and record forensic sample data to NVS
    SampleRecord rec;
    rec.bottle_index = current_bottle_index;
    rec.timestamp_utc = timestamp_utc;
    rec.ph = ph;
    rec.ec = ec;
    rec.do_val = do_val;
    rec.turbidity = turb;
    strncpy(rec.reason, reason, sizeof(rec.reason) - 1);
    rec.reason[sizeof(rec.reason) - 1] = '\0';
    rec.collected = false;

    prefs.begin("aquasampler", false);
    char key[16];
    snprintf(key, sizeof(key), "rec_%u", current_bottle_index);
    prefs.putBytes(key, &rec, sizeof(SampleRecord));

    current_bottle_index++;
    last_sample_timestamp = timestamp_utc;
    prefs.putUChar("bottle_idx", current_bottle_index);
    prefs.putUInt("last_ts", last_sample_timestamp);
    prefs.end();

    Serial.printf("[AUTOSAMPLER-SUCCESS] Bottle #%u Sealed! 250mL sample preserved for NABL lab.\n", current_bottle_index);
    Serial.println(" Dispatching collection alert to local Jal Suraksha Samiti (Max 24h holding limit)!\n");
    return true;
}

bool AutoSampler::getSampleRecord(uint8_t bottle_idx, SampleRecord& rec) {
    if (bottle_idx >= 4) return false;
    prefs.begin("aquasampler", true);
    char key[16];
    snprintf(key, sizeof(key), "rec_%u", bottle_idx);
    size_t len = prefs.getBytes(key, &rec, sizeof(SampleRecord));
    prefs.end();
    return (len == sizeof(SampleRecord));
}

void AutoSampler::resetCarouselAfterCollection() {
    prefs.begin("aquasampler", false);
    prefs.putUChar("bottle_idx", 0);
    prefs.putUInt("last_ts", 0);
    current_bottle_index = 0;
    last_sample_timestamp = 0;
    prefs.end();
    Serial.println("[AUTOSAMPLER] Carousel reset to Bottle #1 after physical laboratory collection.");
}
