#ifndef TELEMETRY_COMM_H
#define TELEMETRY_COMM_H

#include "config.h"
#include "anomaly_engine.h" // SensorReadings, AnomalyResult
#include <ArduinoJson.h>

class TelemetryManager {
public:
    TelemetryManager();
    void init();
    String serializePayload(const SensorReadings& r, const AnomalyResult& anom, uint32_t boot_count,
                            uint8_t bottles_filled);
    bool transmit(const String& payload, bool is_emergency);

private:
    HardwareSerial modemSerial;
};

#endif // TELEMETRY_COMM_H
