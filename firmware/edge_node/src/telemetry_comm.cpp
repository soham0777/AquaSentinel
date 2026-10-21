#include "telemetry_comm.h"

TelemetryManager::TelemetryManager() : modemSerial(2) {}

void TelemetryManager::init() {
    modemSerial.begin(115200, SERIAL_8N1, PIN_MODEM_RX, PIN_MODEM_TX);
}

static const char* riskName(RiskLevel level) {
    switch (level) {
        case RISK_WATCH:        return "WATCH";
        case RISK_EVENT:        return "EVENT";
        case RISK_SENSOR_FAULT: return "SENSOR_FAULT";
        default:                return "NORMAL";
    }
}

String TelemetryManager::serializePayload(const SensorReadings& r, const AnomalyResult& anom, uint32_t cycle,
                                          uint8_t bottles_filled) {
    StaticJsonDocument<768> doc;

    doc["device_id"] = DEVICE_ID;
    doc["fw_ver"] = FIRMWARE_VERSION;
    doc["stretch"] = RIVER_STRETCH_ID;
    doc["cycle"] = cycle; // decision cycle, kept in flash (replaces "boot_seq", which restarted at every reset)
    doc["ts"] = r.timestamp;

    JsonObject data = doc.createNestedObject("telemetry");
    data["ph"] = round(r.ph * 100.0f) / 100.0f;
    data["ec_us"] = round(r.ec * 10.0f) / 10.0f;
    data["do_mg"] = round(r.do_val * 100.0f) / 100.0f;
    data["turb_ntu"] = round(r.turbidity * 10.0f) / 10.0f;
    data["temp_c"] = round(r.temperature * 10.0f) / 10.0f;
    data["stage_m"] = round(r.stage * 100.0f) / 100.0f;
    uint8_t valid_mask = 0; // bit0 pH, bit1 EC, bit2 DO, bit3 turbidity, bit4 temperature, bit5 stage
    for (int i = 0; i < 6; i++) {
        if (r.valid[i]) valid_mask |= (1 << i);
    }
    data["valid"] = valid_mask;
    JsonArray health = data.createNestedArray("health"); // SensorHealthCode bits per channel, same order
    for (int i = 0; i < 6; i++) {
        health.add(r.health[i]);
    }

    JsonObject alert = doc.createNestedObject("anomaly_engine");
    alert["level"] = riskName(anom.level);
    alert["score"] = round(anom.max_score * 100.0f) / 100.0f;
    alert["flags"] = anom.contributing_flags;
    alert["fault_mask"] = anom.fault_mask;
    alert["sample_triggered"] = anom.autosampler_trigger;
    alert["reason"] = anom.reason;
    doc["bottles_filled"] = bottles_filled;

    String output;
    serializeJson(doc, output);
    return output;
}

bool TelemetryManager::transmit(const String& payload, bool is_emergency) {
    if (is_emergency) {
        Serial.println("[TELEMETRY] *** HIGH-PRIORITY EMERGENCY ALERT DISPATCH ***");
        modemSerial.println("ALERT_PRIORITY_HIGH");
    }

    Serial.print("[TELEMETRY] Transmitting frame: ");
    Serial.println(payload);

    modemSerial.println(payload);
    delay(150); // Allow UART buffer flush
    return true;
}
