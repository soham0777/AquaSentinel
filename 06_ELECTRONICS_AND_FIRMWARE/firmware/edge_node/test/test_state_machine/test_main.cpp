/**
 * ==============================================================================
 * AquaSentinel - decision state machine tests (audit P0-3)
 * One bottle per event, a clean end to learning, and learned state that survives a power cut.
 * They run on the ESP32 itself: pio test -e bench
 * Flash writes go to the "aqeng_test" namespace only (config.h), never to the real learned state.
 * ==============================================================================
 */

#include <Arduino.h>
#include <math.h>
#include <Preferences.h>
#include <unity.h>
#include "anomaly_engine.h"
#include "autosampler.h"

static_assert(NVS_SAVE_INTERVAL_CYCLES == 4, "the cycle numbers in test_persist_* assume a 4-cycle save interval");
static_assert(LEARNING_CYCLES > 10, "the learning tests need cycles 1-10 to fall inside the learning period");

static AnomalyEngine engine;
static const uint32_t AFTER_LEARNING = LEARNING_CYCLES + 100;

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

static SensorReadings withEc(float ec) {
    SensorReadings r = healthyReading();
    r.ec = ec;
    return r;
}

static const float EC_SPILL = 3000.0f; // above the 2250 µS/cm hard limit
static const float EC_HIGH = 1500.0f;  // under the hard limit, but z ≈ 20 against the 450 µS/cm baseline

static void clearSavedState() {
    Preferences prefs;
    prefs.begin(ENGINE_NVS_NAMESPACE, false);
    prefs.clear();
    prefs.end();
}

void setUp() {
    clearSavedState();
    engine.resetBaselines();
}
void tearDown() {}

// ---------------------------------------------------------------- one bottle per event (F7, R6)
void test_hard_limit_takes_one_sample_per_event() {
    uint32_t c = AFTER_LEARNING;
    engine.evaluate(healthyReading(), 0, c++);
    int triggers = 0;
    for (int i = 0; i < 6; i++) {
        AnomalyResult res = engine.evaluate(withEc(EC_SPILL), 0, c++);
        TEST_ASSERT_EQUAL_INT(RISK_EVENT, res.level);
        if (res.autosampler_trigger) triggers++;
    }
    TEST_ASSERT_EQUAL_INT(1, triggers); // the old engine triggered on every cycle of the spill
}

void test_tail_under_the_limit_continues_the_event() {
    // The old engine dropped to WATCH on the first tail cycle, then started a "new" event and took a second bottle
    uint32_t c = AFTER_LEARNING;
    engine.evaluate(healthyReading(), 0, c++);
    TEST_ASSERT_TRUE(engine.evaluate(withEc(EC_SPILL), 0, c++).autosampler_trigger);
    TEST_ASSERT_FALSE(engine.evaluate(withEc(EC_SPILL), 0, c++).autosampler_trigger);
    for (int i = 0; i < 6; i++) {
        AnomalyResult res = engine.evaluate(withEc(EC_HIGH), 0, c++);
        TEST_ASSERT_EQUAL_INT(RISK_EVENT, res.level);
        TEST_ASSERT_FALSE(res.autosampler_trigger);
    }
}

void test_flickering_event_takes_one_sample() {
    // Outlier, outlier, then alternating clean and outlier cycles: one event, one bottle
    const bool outlier[] = {true, true, false, true, false, true, false, true, false, true};
    uint32_t c = AFTER_LEARNING;
    engine.evaluate(healthyReading(), 0, c++);
    int triggers = 0;
    for (size_t i = 0; i < sizeof(outlier) / sizeof(outlier[0]); i++) {
        AnomalyResult res = engine.evaluate(outlier[i] ? withEc(EC_HIGH) : healthyReading(), 0, c++);
        if (i >= 1) TEST_ASSERT_EQUAL_INT(RISK_EVENT, res.level);
        if (res.autosampler_trigger) triggers++;
    }
    TEST_ASSERT_EQUAL_INT(1, triggers);
}

void test_new_event_after_recovery_samples_again() {
    uint32_t c = AFTER_LEARNING;
    engine.evaluate(healthyReading(), 0, c++);
    TEST_ASSERT_TRUE(engine.evaluate(withEc(EC_SPILL), 0, c++).autosampler_trigger);
    engine.evaluate(withEc(EC_SPILL), 0, c++);
    for (int i = 0; i < 3; i++) {
        TEST_ASSERT_EQUAL_INT(RISK_EVENT, engine.evaluate(healthyReading(), 0, c++).level);
    }
    TEST_ASSERT_EQUAL_INT(RISK_NORMAL, engine.evaluate(healthyReading(), 0, c++).level); // 4th clean cycle
    AnomalyResult next = engine.evaluate(withEc(EC_SPILL), 0, c++);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, next.level);
    TEST_ASSERT_TRUE(next.autosampler_trigger);
}

// ---------------------------------------------------------------- learning period (F11)
void test_learning_event_clears_after_four_clean_cycles() {
    uint32_t c = 1;
    TEST_ASSERT_TRUE(engine.evaluate(withEc(EC_SPILL), 0, c++).autosampler_trigger);
    for (int i = 0; i < 3; i++) {
        TEST_ASSERT_EQUAL_INT(RISK_EVENT, engine.evaluate(healthyReading(), 0, c++).level);
    }
    TEST_ASSERT_EQUAL_INT(RISK_NORMAL, engine.evaluate(healthyReading(), 0, c++).level);
    TEST_ASSERT_TRUE(engine.evaluate(withEc(EC_SPILL), 0, c++).autosampler_trigger); // a new event samples again
}

void test_no_stale_event_after_learning() {
    // Audit replay: an event at cycle 490 left EVENT latched, so cycles 672-674 reported EVENT on clean water
    const uint32_t spill_at = LEARNING_CYCLES / 2;
    engine.evaluate(withEc(EC_SPILL), 0, spill_at);
    for (uint32_t c = spill_at + 1; c < LEARNING_CYCLES; c++) {
        engine.evaluate(healthyReading(), 0, c);
    }
    for (uint32_t c = LEARNING_CYCLES; c < LEARNING_CYCLES + 3; c++) {
        TEST_ASSERT_EQUAL_INT(RISK_NORMAL, engine.evaluate(healthyReading(), 0, c).level);
    }
}

void test_event_at_the_end_of_learning_still_needs_four_clean_cycles() {
    engine.evaluate(withEc(EC_SPILL), 0, LEARNING_CYCLES - 2);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, engine.evaluate(healthyReading(), 0, LEARNING_CYCLES - 1).level);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, engine.evaluate(healthyReading(), 0, LEARNING_CYCLES).level);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, engine.evaluate(healthyReading(), 0, LEARNING_CYCLES + 1).level);
    TEST_ASSERT_EQUAL_INT(RISK_NORMAL, engine.evaluate(healthyReading(), 0, LEARNING_CYCLES + 2).level);
}

void test_learning_does_not_restart_with_the_counter() {
    // Learning finished (that is saved with the baselines): a cycle counter back at a low number must not
    // switch the statistical track off for another 7 days
    engine.evaluate(healthyReading(), 0, AFTER_LEARNING);
    engine.evaluate(withEc(EC_HIGH), 0, 5);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, engine.evaluate(withEc(EC_HIGH), 0, 6).level);
}

// ---------------------------------------------------------------- flash persistence (F5, R5)
void test_learned_baselines_survive_a_power_cut() {
    for (uint32_t c = 1; c <= 10; c++) {
        engine.evaluate(withEc(600.0f), 0, c); // learning pulls the EC baseline up from 450
    }
    float mu, s, mu_cut, s_cut, mu_back, s_back;
    engine.getBaseline(1, 0, mu, s);
    TEST_ASSERT_TRUE(engine.saveState());
    engine.resetBaselines(); // RAM back at the defaults, as after a power cut
    engine.getBaseline(1, 0, mu_cut, s_cut);
    TEST_ASSERT_TRUE(fabsf(mu_cut - mu) > 1.0f);
    TEST_ASSERT_TRUE(engine.init(false)); // power-on reset: restored from flash
    engine.getBaseline(1, 0, mu_back, s_back);
    TEST_ASSERT_EQUAL_FLOAT(mu, mu_back);
    TEST_ASSERT_EQUAL_FLOAT(s, s_back);
}

void test_reboot_mid_event_takes_no_second_sample() {
    uint32_t c = AFTER_LEARNING;
    engine.evaluate(healthyReading(), 0, c++);
    TEST_ASSERT_TRUE(engine.saveState()); // flash matches RAM before the spill
    TEST_ASSERT_TRUE(engine.evaluate(withEc(EC_SPILL), 0, c).autosampler_trigger);
    TEST_ASSERT_TRUE(engine.persist(c++)); // risk changed: saved at once
    engine.resetBaselines();
    TEST_ASSERT_TRUE(engine.init(false));
    AnomalyResult res = engine.evaluate(withEc(EC_SPILL), 0, c++);
    TEST_ASSERT_EQUAL_INT(RISK_EVENT, res.level);
    TEST_ASSERT_FALSE(res.autosampler_trigger);
}

void test_first_boot_starts_from_defaults() {
    float mu0, s0, mu, s;
    engine.getBaseline(1, 0, mu0, s0);
    for (uint32_t c = 1; c <= 10; c++) {
        engine.evaluate(withEc(600.0f), 0, c);
    }
    TEST_ASSERT_FALSE(engine.init(false)); // nothing in flash: defaults, learning starts again
    engine.getBaseline(1, 0, mu, s);
    TEST_ASSERT_EQUAL_FLOAT(mu0, mu);
}

void test_deep_sleep_wake_keeps_rtc_state() {
    for (uint32_t c = 1; c <= 10; c++) {
        engine.evaluate(withEc(600.0f), 0, c);
    }
    float mu, s, mu_wake, s_wake;
    engine.getBaseline(1, 0, mu, s);
    TEST_ASSERT_TRUE(engine.init(true)); // flash is empty, so this passes only if RTC memory is kept
    engine.getBaseline(1, 0, mu_wake, s_wake);
    TEST_ASSERT_EQUAL_FLOAT(mu, mu_wake);
}

void test_persist_saves_on_change_and_on_the_interval() {
    engine.evaluate(healthyReading(), 0, 1001);
    TEST_ASSERT_TRUE(engine.saveState());                   // flash matches RAM
    TEST_ASSERT_FALSE(engine.persist(1001));                // no change, off the interval: no flash write
    engine.evaluate(healthyReading(), 0, 1002);
    TEST_ASSERT_FALSE(engine.persist(1002));
    engine.evaluate(withEc(EC_SPILL), 0, 1003);             // NORMAL -> EVENT
    TEST_ASSERT_TRUE(engine.persist(1003));
    engine.evaluate(withEc(EC_SPILL), 0, 1004);
    TEST_ASSERT_TRUE(engine.persist(1004));                 // on the interval
    engine.evaluate(withEc(EC_SPILL), 0, 1005);
    TEST_ASSERT_FALSE(engine.persist(1005));
    SensorReadings dead = withEc(EC_SPILL);
    dead.health[0] = HEALTH_TIMEOUT;                        // pH probe stops answering
    dead.valid[0] = false;
    engine.evaluate(dead, 0, 1006);
    TEST_ASSERT_TRUE(engine.persist(1006));                 // fault mask changed
}

// ---------------------------------------------------------------- sampler lockout (F4)
void test_sampler_lockout_counts_cycles() {
    TEST_ASSERT_FALSE(AutoSampler::lockoutActive(10, 0)); // no sample yet
    TEST_ASSERT_TRUE(AutoSampler::lockoutActive(10, 10));
    TEST_ASSERT_TRUE(AutoSampler::lockoutActive(10 + SAMPLE_LOCKOUT_CYCLES - 1, 10));
    TEST_ASSERT_FALSE(AutoSampler::lockoutActive(10 + SAMPLE_LOCKOUT_CYCLES, 10));
    TEST_ASSERT_FALSE(AutoSampler::lockoutActive(5, 10)); // counter restarted below the last sample
}

void setup() {
    delay(2000); // give the serial monitor time to attach
    UNITY_BEGIN();
    RUN_TEST(test_hard_limit_takes_one_sample_per_event);
    RUN_TEST(test_tail_under_the_limit_continues_the_event);
    RUN_TEST(test_flickering_event_takes_one_sample);
    RUN_TEST(test_new_event_after_recovery_samples_again);
    RUN_TEST(test_learning_event_clears_after_four_clean_cycles);
    RUN_TEST(test_no_stale_event_after_learning);
    RUN_TEST(test_event_at_the_end_of_learning_still_needs_four_clean_cycles);
    RUN_TEST(test_learning_does_not_restart_with_the_counter);
    RUN_TEST(test_learned_baselines_survive_a_power_cut);
    RUN_TEST(test_reboot_mid_event_takes_no_second_sample);
    RUN_TEST(test_first_boot_starts_from_defaults);
    RUN_TEST(test_deep_sleep_wake_keeps_rtc_state);
    RUN_TEST(test_persist_saves_on_change_and_on_the_interval);
    RUN_TEST(test_sampler_lockout_counts_cycles);
    UNITY_END();
    clearSavedState(); // leave nothing behind in the test namespace
}

void loop() {}
