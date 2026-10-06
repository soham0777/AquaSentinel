#include "telemetry_comm.h"

TelemetryManager::TelemetryManager() : modemSerial(2) {}

void TelemetryManager::init() {
    modemSerial.begin(115200, SERIAL_8N1, PIN_MODEM_RX, PIN_MODEM_TX);
}

String TelemetryManager::serializePayload(const WaterQualityReading& r, const AnomalyReport& anom, uint32_t boot_count) {
    StaticJsonDocument<512> doc;

    doc["device_id"] = DEVICE_ID;
    doc["fw_ver"] = FIRMWARE_VERSION;
    doc["stretch"] = RIVER_STRETCH_ID;
    doc["boot_seq"] = boot_count;
    doc["ts"] = r.timestamp_epoch;

    JsonObject data = doc.createNestedObject("telemetry");
    data["ph"] = round(r.ph * 100.0f) / 100.0f;
    data["turb_ntu"] = round(r.turbidity_ntu * 10.0f) / 10.0f;
    data["temp_c"] = round(r.temp_c * 10.0f) / 10.0f;
    data["ec_us"] = round(r.ec_us_cm * 10.0f) / 10.0f;
    data["do_mg"] = round(r.do_mg_l * 10.0f) / 10.0f;
    data["depth_m"] = round(r.depth_m * 100.0f) / 100.0f;
    data["v_batt"] = round(r.battery_voltage * 100.0f) / 100.0f;

    JsonObject alert = doc.createNestedObject("anomaly_engine");
    alert["is_alert"] = anom.is_anomaly;
    alert["score"] = round(anom.anomaly_score * 1000.0f) / 1000.0f;
    alert["z_score"] = round(anom.composite_z_score * 10.0f) / 10.0f;
    alert["type"] = anom.alert_description;

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
