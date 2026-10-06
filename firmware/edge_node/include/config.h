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

#endif // CONFIG_H
