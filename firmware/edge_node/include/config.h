/**
 * ==============================================================================
 * AquaSentinel v2.0 - Edge Controller Pinout & Hardware Configuration
 * Project: AquaRight | Competition: AAKRUTI Innovation Competition (AIC) 2026
 * Theme: Robotics | Institution: Sanjivani University, Kopargaon
 * ==============================================================================
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// -----------------------------------------------------------------------------
// 1. Hardware Pin Allocations (Appendix A - Verified Netlist)
// Strictly avoids ESP32 strapping pins (0, 2, 12, 15) for active outputs
// -----------------------------------------------------------------------------

// Cellular Modem (SIMCom A7670C LTE Cat-1)
#define PIN_MODEM_TX          17  // ESP32 TX2 -> Modem RXD
#define PIN_MODEM_RX          16  // ESP32 RX2 <- Modem TXD
#define PIN_MODEM_PWRKEY      4   // Active-LOW Pulse to power on/off modem

// RS485 Multi-Probe Bus (SP3485 Half-Duplex Transceiver)
#define PIN_RS485_TX          27  // ESP32 TX1 -> SP3485 DI
#define PIN_RS485_RX          26  // ESP32 RX1 <- SP3485 RO
#define PIN_RS485_DE_RE       25  // Direction Control: HIGH=TX, LOW=RX

// MicroSD Local SPI Interface (VSPI Bus)
#define PIN_SD_SCK           18  // VSPI Clock (10k pull-up)
#define PIN_SD_MISO          19  // VSPI MISO  (10k pull-up)
#define PIN_SD_MOSI          23  // VSPI MOSI  (10k pull-up)
#define PIN_SD_CS            5   // VSPI Chip Select (10k pull-up)

// I2C Precision Bus (DS3231SN RTC, INA226 Monitor, PCA9685 Controller)
#define PIN_I2C_SDA          21  // I2C Serial Data
#define PIN_I2C_SCL          22  // I2C Serial Clock (4.7k pull-up)

// Ultrasonic Water Level / Stage Sensor (JSN-SR04T)
#define PIN_STAGE_RX         34  // Input-only pin (Safe software UART RX)

// Switched Power Rails (Gated via P-MOSFET Load Switches - Active LOW)
#define PIN_EN_12V_SENSOR    32  // Gate driver for 12V RS485 Sensor Bus
#define PIN_EN_4V_MODEM      33  // Gate driver for 4.0V / 2A Cellular Buck
#define PIN_EN_5V_PERIPH     13  // Gate driver for 5.0V PCA9685 & Servos
#define PIN_EN_12V_PUMP      14  // Low-side N-MOSFET for 12V Peristaltic Pump
#define PIN_CAROUSEL_IRQ     35  // Input-only pin: Optical Limit Switch Pulse

// System Status LED
#define PIN_STATUS_LED       2   // Onboard diagnostic LED (Active HIGH)

// -----------------------------------------------------------------------------
// 2. PCA9685 I2C 16-Channel PWM Channel Assignments (I2C Addr: 0x40)
// -----------------------------------------------------------------------------
#define PWM_CH_BEACON_RED     0   // Jal-Deep 360° Safety Beacon - Red Channel
#define PWM_CH_BEACON_GREEN   1   // Jal-Deep 360° Safety Beacon - Green Channel
#define PWM_CH_BEACON_BLUE    2   // Jal-Deep 360° Safety Beacon - Blue Channel
#define PWM_CH_WIPER_SERVO    3   // Motorized Optical Sensor Wiper (50Hz PWM)
#define PWM_CH_CAROUSEL_PWM   4   // Autosampler Carousel Geared Motor Speed
#define PWM_CH_PINCH_VALVE    5   // Autosampler 3-Way Purge Pinch Valve Gate

// -----------------------------------------------------------------------------
// 3. Modbus Slave ID Addresses (RS485 Industrial Probes)
// -----------------------------------------------------------------------------
#define MODBUS_ID_PH          0x01 // DFRobot SEN0708 Industrial pH Probe
#define MODBUS_ID_EC          0x02 // DFRobot SEN0707 Industrial EC Probe (K=10)
#define MODBUS_ID_DO          0x03 // DFRobot SEN0680 Optical Luminescent DO Probe
#define MODBUS_ID_TURBIDITY   0x04 // DFRobot SEN0710 Nephelometric Turbidity Probe

// -----------------------------------------------------------------------------
// 4. Operational Timing & Energy Budget Constraints
// -----------------------------------------------------------------------------
#define SAMPLING_INTERVAL_MIN 15   // 15-minute standard sampling interval
#define SENSOR_WARMUP_MS      30000// 30-second probe pre-warmup stabilization
#define PURGE_DURATION_MS     20000// 20-second reverse purge before vial draw
#define FILL_DURATION_MS      30000// 30-second vial fill time (~250 mL capture)
#define WIPER_INTERVAL_HOURS  6    // Sweep optical wiper every 6 hours
#define SAMPLE_LOCKOUT_MIN    60   // 60-minute lockout between physical captures

// -----------------------------------------------------------------------------
// 5. CPCB Designated Best Use Class C Hard Limit Tripwires
// -----------------------------------------------------------------------------
#define LIMIT_PH_MIN          6.0f
#define LIMIT_PH_MAX          9.0f
#define LIMIT_DO_MIN          4.0f  // mg/L minimum dissolved oxygen
#define LIMIT_EC_MAX          2250.0f // µS/cm maximum conductivity

// -----------------------------------------------------------------------------
// 6. Device Identity (telemetry frames and the evidence log)
// Override per float with build flags, e.g. -D DEVICE_ID='"AQS-02"'
// -----------------------------------------------------------------------------
#ifndef FIRMWARE_VERSION
#define FIRMWARE_VERSION      "2.1.0-dev"          // 2.1 = first version that compiles (audit P0-1)
#endif
#ifndef DEVICE_ID
#define DEVICE_ID             "AQS-DEV-01"         // set before deployment
#endif
#ifndef RIVER_STRETCH_ID
#define RIVER_STRETCH_ID      "GODAVARI-KOPARGAON" // monitored river stretch
#endif

// -----------------------------------------------------------------------------
// 7. Fitted Sensor Channels (bit order shared with SensorReadings.health[])
// A channel that is not fitted is not polled and never raises a sensor fault.
// Water temperature comes from the pH probe's reply.
// -----------------------------------------------------------------------------
#define SENSOR_BIT_PH         (1 << 0)
#define SENSOR_BIT_EC         (1 << 1)
#define SENSOR_BIT_DO         (1 << 2)
#define SENSOR_BIT_TURB       (1 << 3)
#define SENSOR_BIT_TEMP       (1 << 4)
#define SENSOR_BIT_STAGE      (1 << 5)  // no stage driver yet (audit F4): leave unfitted

#ifndef SENSORS_FITTED
#ifdef BENCH_DEMO
#define SENSORS_FITTED        (SENSOR_BIT_EC) // bench demo: the EC probe only
#else
#define SENSORS_FITTED        (SENSOR_BIT_PH | SENSOR_BIT_EC | SENSOR_BIT_DO | SENSOR_BIT_TURB | SENSOR_BIT_TEMP)
#endif
#endif

// -----------------------------------------------------------------------------
// 8. Modbus-RTU Timing (DFRobot: polling interval and response wait both above 200 ms)
// -----------------------------------------------------------------------------
#define MODBUS_RESPONSE_TIMEOUT_MS 300
#define MODBUS_POLL_GAP_MS         250

// -----------------------------------------------------------------------------
// 9. Plausible Ranges: a reading outside them is flagged HEALTH_OUT_OF_BOUNDS and never used.
// Confirm each against its datasheet when the probes are commissioned (BENCH_DEMO_PLAN.md, P1-8).
// -----------------------------------------------------------------------------
#define RANGE_PH_MIN          0.0f     // pH scale
#define RANGE_PH_MAX          14.0f
#define RANGE_EC_MIN          10.0f    // µS/cm; SEN0707 (K=10) measures 10-20,000. Lower: out of water, or pure water
#define RANGE_EC_MAX          20000.0f
#define RANGE_DO_MIN          0.0f     // mg/L
#define RANGE_DO_MAX          20.0f    // saturation is about 14.6 mg/L at 0 °C; margin for supersaturation
#define RANGE_TURB_MIN        0.0f     // NTU; SEN0710 measures 0-1000
#define RANGE_TURB_MAX        1000.0f
#define RANGE_TEMP_MIN        -20.0f   // °C; probe operating range -20 to +60
#define RANGE_TEMP_MAX        60.0f

// -----------------------------------------------------------------------------
// 10. Decision State and Flash Persistence (audit F5, F7, F11)
// Counted in decision cycles, which are kept in flash: the clock is not reliable yet (audit F4).
// -----------------------------------------------------------------------------
#define LEARNING_CYCLES          (7UL * 24 * 60 / SAMPLING_INTERVAL_MIN)            // 7 days: 672 at 15 min
#define SAMPLE_LOCKOUT_CYCLES    (SAMPLE_LOCKOUT_MIN / SAMPLING_INTERVAL_MIN)       // 60 min: 4 cycles
#define WIPER_INTERVAL_CYCLES    (WIPER_INTERVAL_HOURS * 60 / SAMPLING_INTERVAL_MIN) // 6 h: 24 cycles
#define NVS_SAVE_INTERVAL_CYCLES 4   // learned state saved at least hourly, and at once on a risk or fault change
#define NODE_NVS_NAMESPACE       "aquanode"   // decision cycle counter
#ifdef PIO_UNIT_TESTING
#define ENGINE_NVS_NAMESPACE     "aqeng_test" // unit tests never overwrite the real learned state
#else
#define ENGINE_NVS_NAMESPACE     "aquaengine" // baselines, learning progress, risk state
#endif

#endif // CONFIG_H
