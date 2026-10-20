#include "microsd_logger.h"

MicroSDLogger::MicroSDLogger() : is_available(false) {}

bool MicroSDLogger::init() {
    SPI.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
    if (!SD.begin(PIN_SD_CS)) {
        Serial.println("[SD] Failed to mount MicroSD filesystem! Operating in memory-only fallback.");
        is_available = false;
        return false;
    }
    Serial.println("[SD] MicroSD mounted successfully (Industrial FAT32).");
    is_available = true;
    writeHeaderIfNew();
    return true;
}

void MicroSDLogger::writeHeaderIfNew() {
    if (!is_available) return;
    if (!SD.exists(log_filename)) {
        File f = SD.open(log_filename, FILE_WRITE);
        if (f) {
            f.println("timestamp,ph,ec_us_cm,do_mg_l,turbidity_ntu,temp_c,stage_m,valid_mask,risk_level,max_score,flags,sampler_trigger,reason");
            f.flush();
            f.close();
            Serial.println("[SD] Created new log file with header.");
        }
    }
}

bool MicroSDLogger::logReading(const SensorReadings& r, const AnomalyResult& anom) {
    if (!is_available) return false;

    File f = SD.open(log_filename, FILE_APPEND);
    if (!f) {
        Serial.println("[SD] Error opening log file for append!");
        return false;
    }

    uint8_t valid_mask = 0; // bit0 pH, bit1 EC, bit2 DO, bit3 turbidity, bit4 temperature, bit5 stage
    for (int i = 0; i < 6; i++) {
        if (r.valid[i]) valid_mask |= (1 << i);
    }

    f.printf("%lu,%.2f,%.1f,%.2f,%.1f,%.1f,%.2f,0x%02X,%d,%.2f,0x%02X,%d,\"%s\"\n",
        (unsigned long)r.timestamp,
        r.ph,
        r.ec,
        r.do_val,
        r.turbidity,
        r.temperature,
        r.stage,
        valid_mask,
        (int)anom.level,
        anom.max_score,
        anom.contributing_flags,
        anom.autosampler_trigger ? 1 : 0,
        anom.reason
    );

    f.flush(); // Push the line to the card; FAT writes are not atomic
    f.close();
    return true;
}

bool MicroSDLogger::queueBacklog(const char* json_payload) {
    if (!is_available) return false;
    File f = SD.open(backlog_filename, FILE_APPEND);
    if (!f) return false;
    f.println(json_payload);
    f.flush();
    f.close();
    Serial.println("[SD] Enqueued unsent telemetry record to local backlog queue.");
    return true;
}

int MicroSDLogger::getBacklogCount() {
    if (!is_available || !SD.exists(backlog_filename)) return 0;
    File f = SD.open(backlog_filename, FILE_READ);
    if (!f) return 0;
    int count = 0;
    while (f.available()) {
        if (f.read() == '\n') count++;
    }
    f.close();
    return count;
}

String MicroSDLogger::popBacklogRecord() {
    if (!is_available || !SD.exists(backlog_filename)) return "";
    File f = SD.open(backlog_filename, FILE_READ);
    if (!f) return "";
    String record = f.readStringUntil('\n');
    f.close();
    return record;
}
