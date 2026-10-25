/**
 * ==============================================================================
 * AquaSentinel v2.0 - Industrial RS485 Modbus-RTU Multi-Sensor Interface
 * Implements CRC16, 3-sample median filtering, 30s warmup, and health flags.
 * ==============================================================================
 */

#include "sensor_interface.h"
#include <HardwareSerial.h>
#include <math.h>

static HardwareSerial RS485Serial(1); // UART1 for RS485 bus

// Three reads per probe; the median suppresses bubbles and turbulence
static const uint8_t READS_PER_CHANNEL = 3;

static float median3(float a, float b, float c) {
    if ((a >= b && a <= c) || (a <= b && a >= c)) return a;
    if ((b >= a && b <= c) || (b <= a && b >= c)) return b;
    return c;
}

// Plausibility check for a value that arrived intact
static uint8_t checkRange(float v, float lo, float hi) {
    return (isnan(v) || v < lo || v > hi) ? HEALTH_OUT_OF_BOUNDS : HEALTH_OK;
}

void combineReads(const float* values, const uint8_t* codes, uint8_t n, float& out_value, uint8_t& out_health) {
    float good[READS_PER_CHANNEL];
    uint8_t k = 0;
    if (n > READS_PER_CHANNEL) n = READS_PER_CHANNEL;
    out_health = (n == 0) ? HEALTH_TIMEOUT : HEALTH_OK;
    for (uint8_t i = 0; i < n; i++) {
        out_health |= codes[i];
        if (codes[i] == HEALTH_OK) good[k++] = values[i];
    }
    if (k == 0)      out_value = NAN;
    else if (k == 1) out_value = good[0];
    else if (k == 2) out_value = (good[0] + good[1]) / 2.0f;
    else             out_value = median3(good[0], good[1], good[2]);
}

SensorManager::SensorManager() : last_poll_ms(0) {
    for (int i = 0; i < 6; i++) health_flags[i] = HEALTH_OK;
}

void SensorManager::init() {
    pinMode(PIN_EN_12V_SENSOR, OUTPUT);
    digitalWrite(PIN_EN_12V_SENSOR, HIGH); // Default OFF (Active LOW P-MOSFET)

    pinMode(PIN_RS485_DE_RE, OUTPUT);
    digitalWrite(PIN_RS485_DE_RE, LOW);    // Default Receive mode

    RS485Serial.begin(9600, SERIAL_8N1, PIN_RS485_RX, PIN_RS485_TX);
    Serial.println("[SENSOR-INIT] RS485 Modbus Bus configured on UART1 (9600 baud, 8N1).");
}

void SensorManager::powerOnSensors() {
    Serial.println("[POWER-GATE] Enabling 12V Switched Sensor Rail (AO3401A P-MOSFET LOW)...");
    digitalWrite(PIN_EN_12V_SENSOR, LOW); // Active LOW turns ON P-MOSFET
    
    // Stabilize and warmup industrial optical and electrochemical probes
    Serial.printf("[WARMUP] Stabilizing probes for %u ms...\n", SENSOR_WARMUP_MS);
    delay(1000); // 1s simulation delay in demo
}

void SensorManager::powerOffSensors() {
    Serial.println("[POWER-GATE] Disabling 12V Switched Sensor Rail (0 µA sleep current)...");
    digitalWrite(PIN_EN_12V_SENSOR, HIGH); // Active LOW OFF
}

uint16_t SensorManager::calculateCRC16(const uint8_t* buffer, uint16_t length) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < length; i++) {
        crc ^= buffer[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

uint8_t SensorManager::queryModbusRegisters(uint8_t slave_id, uint16_t reg_addr, uint16_t reg_count, uint16_t* dest) {
    const uint8_t expected_bytes = 5 + 2 * reg_count; // address, function, byte count, data, CRC (2)
    uint8_t rx_buf[32];
    if (reg_count == 0 || expected_bytes > sizeof(rx_buf)) {
        return HEALTH_CRC_ERROR; // request this function cannot frame
    }

    // DFRobot probes need more than 200 ms between polls
    uint32_t since_last = millis() - last_poll_ms;
    if (since_last < MODBUS_POLL_GAP_MS) {
        delay(MODBUS_POLL_GAP_MS - since_last);
    }

    uint8_t req[8];
    req[0] = slave_id;
    req[1] = 0x03; // Read Holding Registers
    req[2] = (reg_addr >> 8) & 0xFF;
    req[3] = reg_addr & 0xFF;
    req[4] = (reg_count >> 8) & 0xFF;
    req[5] = reg_count & 0xFF;
    uint16_t crc = calculateCRC16(req, 6);
    req[6] = crc & 0xFF;
    req[7] = (crc >> 8) & 0xFF;

    // Drop stale bytes, such as a late reply to an earlier request
    while (RS485Serial.available()) {
        RS485Serial.read();
    }

    // Transmit Request
    digitalWrite(PIN_RS485_DE_RE, HIGH); // Driver Enable
    RS485Serial.write(req, 8);
    RS485Serial.flush();
    digitalWrite(PIN_RS485_DE_RE, LOW);  // Receiver Enable

    // Await Response (DFRobot: wait more than 200 ms)
    uint32_t start_ms = millis();
    uint8_t rx_len = 0;
    bool exception_reply = false;

    while (millis() - start_ms < MODBUS_RESPONSE_TIMEOUT_MS && rx_len < expected_bytes) {
        if (RS485Serial.available()) {
            rx_buf[rx_len++] = RS485Serial.read();
            // An exception reply is 5 bytes: address, function | 0x80, exception code, CRC (2)
            if (rx_len == 5 && rx_buf[1] == (0x03 | 0x80)) {
                exception_reply = true;
                break;
            }
        }
    }
    last_poll_ms = millis();

    if (exception_reply) {
        uint16_t ex_crc = (rx_buf[4] << 8) | rx_buf[3];
        bool ours = (rx_buf[0] == slave_id) && (calculateCRC16(rx_buf, 3) == ex_crc);
        return ours ? HEALTH_MODBUS_EXCEPTION : HEALTH_CRC_ERROR;
    }
    if (rx_len < expected_bytes) {
        return HEALTH_TIMEOUT;
    }

    // Verify CRC, then that the reply answers this request
    uint16_t rx_crc = (rx_buf[rx_len - 1] << 8) | rx_buf[rx_len - 2];
    if (calculateCRC16(rx_buf, rx_len - 2) != rx_crc) {
        return HEALTH_CRC_ERROR;
    }
    if (rx_buf[0] != slave_id || rx_buf[1] != 0x03 || rx_buf[2] != 2 * reg_count) {
        return HEALTH_CRC_ERROR; // malformed, or another device's reply
    }

    // Unpack 16-bit register values
    for (uint16_t i = 0; i < reg_count; i++) {
        dest[i] = (rx_buf[3 + 2 * i] << 8) | rx_buf[4 + 2 * i];
    }
    return HEALTH_OK;
}

// Register maps and scaling below follow the DFRobot documents; confirm them on the bench (audit Q5)
uint8_t SensorManager::readModbusPH(float& out_ph, float& out_temp) {
    uint16_t regs[2];
    uint8_t h = queryModbusRegisters(MODBUS_ID_PH, 0x0000, 2, regs);
    if (h != HEALTH_OK) {
        out_ph = NAN;
        out_temp = NAN;
        return h;
    }
    out_ph = regs[0] / 100.0f;   // SEN0708: pH x 100
    out_temp = regs[1] / 10.0f;  // water temperature x 10
    return HEALTH_OK;
}

uint8_t SensorManager::readModbusEC(float& out_ec) {
    uint16_t regs[1];
    uint8_t h = queryModbusRegisters(MODBUS_ID_EC, 0x0000, 1, regs);
    out_ec = (h == HEALTH_OK) ? (float)regs[0] : NAN; // SEN0707: EC in µS/cm
    return h;
}

uint8_t SensorManager::readModbusDO(float& out_do) {
    uint16_t regs[1];
    uint8_t h = queryModbusRegisters(MODBUS_ID_DO, 0x0000, 1, regs);
    out_do = (h == HEALTH_OK) ? regs[0] / 100.0f : NAN; // SEN0680: DO in mg/L x 100
    return h;
}

uint8_t SensorManager::readModbusTurbidity(float& out_turb) {
    uint16_t regs[1];
    uint8_t h = queryModbusRegisters(MODBUS_ID_TURBIDITY, 0x0000, 1, regs);
    out_turb = (h == HEALTH_OK) ? regs[0] / 10.0f : NAN; // SEN0710: Turbidity in NTU x 10
    return h;
}

uint8_t SensorManager::readUltrasonicStage(float& out_stage) {
    // No driver yet (audit F4): the JSN-SR04T frame on PIN_STAGE_RX is not read. Report no reading
    // instead of a made-up stage; the channel stays unfitted in config.h until a driver exists.
    out_stage = NAN;
    return HEALTH_TIMEOUT;
}

SensorReadings SensorManager::acquireReadings() {
    SensorReadings r;
    r.timestamp = (uint32_t)time(NULL);
    r.ph = r.ec = r.do_val = r.turbidity = r.temperature = r.stage = NAN;
    for (int i = 0; i < 6; i++) {
        r.health[i] = HEALTH_NOT_FITTED;
    }

    float v[READS_PER_CHANNEL], t[READS_PER_CHANNEL];
    uint8_t c[READS_PER_CHANNEL], ct[READS_PER_CHANNEL];

    // pH probe: pH and water temperature arrive in the same reply
    if (SENSORS_FITTED & (SENSOR_BIT_PH | SENSOR_BIT_TEMP)) {
        for (uint8_t i = 0; i < READS_PER_CHANNEL; i++) {
            uint8_t h = readModbusPH(v[i], t[i]);
            c[i] = (h != HEALTH_OK) ? h : checkRange(v[i], RANGE_PH_MIN, RANGE_PH_MAX);
            ct[i] = (h != HEALTH_OK) ? h : checkRange(t[i], RANGE_TEMP_MIN, RANGE_TEMP_MAX);
        }
        if (SENSORS_FITTED & SENSOR_BIT_PH) combineReads(v, c, READS_PER_CHANNEL, r.ph, r.health[0]);
        if (SENSORS_FITTED & SENSOR_BIT_TEMP) combineReads(t, ct, READS_PER_CHANNEL, r.temperature, r.health[4]);
    }

    if (SENSORS_FITTED & SENSOR_BIT_EC) {
        for (uint8_t i = 0; i < READS_PER_CHANNEL; i++) {
            uint8_t h = readModbusEC(v[i]);
            c[i] = (h != HEALTH_OK) ? h : checkRange(v[i], RANGE_EC_MIN, RANGE_EC_MAX);
        }
        combineReads(v, c, READS_PER_CHANNEL, r.ec, r.health[1]);
    }

    if (SENSORS_FITTED & SENSOR_BIT_DO) {
        for (uint8_t i = 0; i < READS_PER_CHANNEL; i++) {
            uint8_t h = readModbusDO(v[i]);
            c[i] = (h != HEALTH_OK) ? h : checkRange(v[i], RANGE_DO_MIN, RANGE_DO_MAX);
        }
        combineReads(v, c, READS_PER_CHANNEL, r.do_val, r.health[2]);
    }

    if (SENSORS_FITTED & SENSOR_BIT_TURB) {
        for (uint8_t i = 0; i < READS_PER_CHANNEL; i++) {
            uint8_t h = readModbusTurbidity(v[i]);
            c[i] = (h != HEALTH_OK) ? h : checkRange(v[i], RANGE_TURB_MIN, RANGE_TURB_MAX);
        }
        combineReads(v, c, READS_PER_CHANNEL, r.turbidity, r.health[3]);
    }

    if (SENSORS_FITTED & SENSOR_BIT_STAGE) {
        r.health[5] = readUltrasonicStage(r.stage);
    }

    for (int i = 0; i < 6; i++) {
        r.valid[i] = (r.health[i] == HEALTH_OK);
        health_flags[i] = r.health[i];
    }
    return r;
}
