#ifndef TELEMETRY_COMM_H
#define TELEMETRY_COMM_H

#include "config.h"
#include <ArduinoJson.h>

class TelemetryManager {
public:
    TelemetryManager();
    void init();
    String serializePayload(const WaterQualityReading& r, const AnomalyReport& anom, uint32_t boot_count);
    bool transmit(const String& payload, bool is_emergency);

private:
    HardwareSerial modemSerial;
};

#endif // TELEMETRY_COMM_H
