#ifndef MICROSD_LOGGER_H
#define MICROSD_LOGGER_H

#include "config.h"
#include "anomaly_engine.h" // SensorReadings, AnomalyResult
#include <SPI.h>
#include <FS.h>
#include <SD.h>

class MicroSDLogger {
public:
    MicroSDLogger();
    bool init();
    bool logReading(const SensorReadings& r, const AnomalyResult& anom);
    bool queueBacklog(const char* json_payload);
    int getBacklogCount();
    String popBacklogRecord();

private:
    bool is_available;
    const char* log_filename = "/aquasentinel_log.csv";
    const char* backlog_filename = "/backlog_queue.txt";
    void writeHeaderIfNew();
};

#endif // MICROSD_LOGGER_H
