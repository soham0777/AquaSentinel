/**
 * ==============================================================================
 * AquaSentinel - fail-safe sensing tests (audit P0-2)
 * A dead or missing probe must never read as clean water.
 * They run on the ESP32 itself: pio test -e bench
 * ==============================================================================
 */

#include <Arduino.h>
#include <math.h>
#include <unity.h>
#include "anomaly_engine.h"
#include "sensor_interface.h"

static AnomalyEngine engine;

// A complete, healthy reading at the engine's cold-boot baselines; the stage is not fitted
static SensorReadings healthyReading() {
    SensorReadings r;
    r.ph = 7.5f;
    r.ec = 450.0f;
    r.do_val = 6.5f;
    r.turbidity = 12.0f;
    r.temperature = 24.0f;
    r.stage = NAN;
    r.timestamp = 0;
    for (int i = 0; i < 6; i++) {
        r.health[i] = HEALTH_OK;
        r.valid[i] = true;
    }
    r.health[5] = HEALTH_NOT_FITTED;
    r.valid[5] = false;
    return r;
}

static void failChannel(SensorReadings& r, int ch, uint8_t code, float value = NAN) {
    r.health[ch] = code;
    r.valid[ch] = false;
    switch (ch) {
        case 0: r.ph = value; break;
        case 1: r.ec = value; break;
        case 2: r.do_val = value; break;
        case 3: r.turbidity = value; break;
        case 4: r.temperature = value; break;
        default: r.stage = value; break;
    }
}

void setUp() { engine.resetBaselines(); }
void tearDown() {}

// ---------------------------------------------------------------- combineReads
void test_three_good_reads_give_the_median() {
    float v[3] = {7.1f, 7.3f, 7.2f};
    uint8_t c[3] = {HEALTH_OK, HEALTH_OK, HEALTH_OK};
    float out;
    uint8_t h;
    combineReads(v, c, 3, out, h);
    TEST_ASSERT_EQUAL_UINT8(HEALTH_OK, h);
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 7.2f, out);
}

void test_one_failed_read_makes_the_channel_invalid() {
    // The old code marked this case valid when the last read happened to succeed (audit F2)
    float v[3] = {7.1f, NAN, 7.3f};
    uint8_t c[3] = {HEALTH_OK, HEALTH_TIMEOUT, HEALTH_OK};
    float out;
    uint8_t h;
    combineReads(v, c, 3, out, h);
    TEST_ASSERT_EQUAL_UINT8(HEALTH_TIMEOUT, h);
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 7.2f, out); // kept for the log, but not trusted
}

void test_no_good_read_gives_nan() {
    float v[3] = {NAN, NAN, NAN};
    uint8_t c[3] = {HEALTH_TIMEOUT, HEALTH_CRC_ERROR, HEALTH_TIMEOUT};
    float out;
    uint8_t h;
    combineReads(v, c, 3, out, h);
    TEST_ASSERT_TRUE(isnan(out));
    TEST_ASSERT_EQUAL_UINT8(HEALTH_TIMEOUT | HEALTH_CRC_ERROR, h);
}

// ---------------------------------------------------------------- engine
void test_healthy_reading_stays_normal() {
    AnomalyResult res = engine.evaluate(healthyReading(), 0, 1000);
    TEST_ASSERT_EQUAL_INT(RISK_NORMAL, res.level);
    TEST_ASSERT_EQUAL_UINT8(0, res.fault_mask);
    TEST_ASSERT_FALSE(res.fault_onset);
}

void test_dead_probe_is_a_fault_never_normal() {
    SensorReadings r = healthyReading();
    failChannel(r, 1, HEALTH_TIMEOUT); // EC probe silent
    AnomalyResult res = engine.evaluate(r, 0, 1000);
    TEST_ASSERT_EQUAL_INT(RISK_SENSOR_FAULT, res.level);
    TEST_ASSERT_EQUAL_UINT8(1 << 1, res.fault_mask);
}

void test_dead_probe_during_learning_is_a_fault() {
    SensorReadings r = healthyReading();
    failChannel(r, 0, HEALTH_CRC_ERROR);
    AnomalyResult res = engine.evaluate(r, 0, 10);
    TEST_ASSERT_EQUAL_INT(RISK_SENSOR_FAULT, res.level);
}

void test_every_probe_dead_is_a_fault() {
    // Audit scenario B: with every probe failing, the old engine reported NORMAL and missed all four spills
    SensorReadings r = healthyReading();
    for (int ch = 0; ch < 5; ch++) {
        failChannel(r, ch, HEALTH_TIMEOUT);
    }
    AnomalyResult res = engine.evaluate(r, 0, 1000);
    TEST_ASSERT_EQUAL_INT(RISK_SENSOR_FAULT, res.level);
    TEST_ASSERT_EQUAL_UINT8(0x1F, res.fault_mask);
}

void test_unfitted_channels_are_not_faults() {
    // The bench build fits the EC probe only
    SensorReadings r = healthyReading();
    const int unfitted[] = {0, 2, 3, 4};
    for (int ch : unfitted) {
        failChannel(r, ch, HEALTH_NOT_FITTED);
    }
    AnomalyResult res = engine.evaluate(r, 0, 1000);
    TEST_ASSERT_EQUAL_UINT8(0, res.fault_mask);
    TEST_ASSERT_EQUAL_INT(RISK_NORMAL, res.level);
}

void test_invalid_value_never_enters_the_baseline() {
    float mu0, s0, mu1, s1;
    engine.getBaseline(1, 0, mu0, s0);
    SensorReadings r = healthyReading();
    failChannel(r, 1, HEALTH_OUT_OF_BOUNDS, 25000.0f); // garbage value, flagged invalid
    engine.evaluate(r, 0, 10);                          // learning: valid channels update their baselines
    engine.getBaseline(1, 0, mu1, s1);
    TEST_ASSERT_EQUAL_FLOAT(mu0, mu1);
    TEST_ASSERT_EQUAL_FLOAT(s0, s1);
}

void test_invalid_value_cannot_trip_a_hard_limit() {
    SensorReadings r = healthyReading();
    failChannel(r, 1, HEALTH_CRC_ERROR, 9999.0f); // above the 2250 µS/cm limit, but untrusted
    AnomalyResult res = engine.evaluate(r, 0, 1000);
    TEST_ASSERT_EQUAL_INT(RISK_SENSOR_FAULT, res.level);
    TEST_ASSERT_FALSE(res.autosampler_trigger);
}

void test_spill_on_a_working_probe_beats_a_fault_elsewhere() {
    SensorReadings r = healthyReading();
    r.ph = 4.0f;                       // acid spill on a working pH probe
    failChannel(r, 2, HEALTH_TIMEOUT); // DO probe silent
    AnomalyResult res = engine.evaluate(r, 0, 1000);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, res.level);
    TEST_ASSERT_TRUE(res.autosampler_trigger);
    TEST_ASSERT_EQUAL_UINT8(1 << 2, res.fault_mask);
}

void test_fault_alert_is_flagged_once() {
    SensorReadings bad = healthyReading();
    failChannel(bad, 1, HEALTH_TIMEOUT);
    TEST_ASSERT_TRUE(engine.evaluate(bad, 0, 1000).fault_onset);
    TEST_ASSERT_FALSE(engine.evaluate(bad, 0, 1001).fault_onset); // still faulted: no repeat alert
    engine.evaluate(healthyReading(), 0, 1002);                   // probe recovers
    TEST_ASSERT_TRUE(engine.evaluate(bad, 0, 1003).fault_onset);  // fails again: alert again
}

void setup() {
    delay(2000); // give the serial monitor time to attach
    UNITY_BEGIN();
    RUN_TEST(test_three_good_reads_give_the_median);
    RUN_TEST(test_one_failed_read_makes_the_channel_invalid);
    RUN_TEST(test_no_good_read_gives_nan);
    RUN_TEST(test_healthy_reading_stays_normal);
    RUN_TEST(test_dead_probe_is_a_fault_never_normal);
    RUN_TEST(test_dead_probe_during_learning_is_a_fault);
    RUN_TEST(test_every_probe_dead_is_a_fault);
    RUN_TEST(test_unfitted_channels_are_not_faults);
    RUN_TEST(test_invalid_value_never_enters_the_baseline);
    RUN_TEST(test_invalid_value_cannot_trip_a_hard_limit);
    RUN_TEST(test_spill_on_a_working_probe_beats_a_fault_elsewhere);
    RUN_TEST(test_fault_alert_is_flagged_once);
    UNITY_END();
}

void loop() {}
