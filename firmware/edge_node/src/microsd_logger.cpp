#include "microsd_logger.h"

MicroSDLogger::MicroSDLogger() : is_available(false) {}

bool MicroSDLogger::init() {
    SPI.begin(PIN_SPI_SCK, PIN_SPI_MISO, PIN_SPI_MOSI, PIN_SD_CS);
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
            f.println("epoch_timestamp,ph,turbidity_ntu,temp_c,ec_us_cm,do_mg_l,depth_m,battery_v,anomaly_score,is_anomaly,alert_desc");
            f.flush();
            f.close();
            Serial.println("[SD] Created new log file with header.");
        }
    }
}

bool MicroSDLogger::logReading(const WaterQualityReading& r, const AnomalyReport& anom) {
    if (!is_available) return false;

    File f = SD.open(log_filename, FILE_APPEND);
    if (!f) {
        Serial.println("[SD] Error opening log file for append!");
        return false;
    }

    f.printf("%u,%.3f,%.2f,%.2f,%.1f,%.2f,%.3f,%.2f,%.3f,%d,%s\n",
        r.timestamp_epoch,
        r.ph,
        r.turbidity_ntu,
        r.temp_c,
        r.ec_us_cm,
        r.do_mg_l,
        r.depth_m,
        r.battery_voltage,
        anom.anomaly_score,
        anom.is_anomaly ? 1 : 0,
        anom.alert_description
    );

    f.flush(); // Atomic sector commit
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
