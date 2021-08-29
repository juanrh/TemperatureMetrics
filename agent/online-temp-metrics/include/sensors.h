// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE
#ifndef AGENT_ONLINE_TEMP_METRICS_INCLUDE_SENSOR_H_
#define AGENT_ONLINE_TEMP_METRICS_INCLUDE_SENSOR_H_

#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <variant>

extern "C" {
    #include "sht31_sensor.h"
}

struct Measurement {
    // Celsius degrees
    double temperature;
    double humidity;

    friend std::ostream& operator<<(std::ostream& os, const Measurement& measurement);
};

class Sensor {
 public:
    // FIXME: pass exception or something with the error code
    virtual std::variant<Measurement, std::string> measure() = 0;
};

class Sht31Sensor : public Sensor {
 public:
    explicit Sht31Sensor(int busNumber);
    Sht31Sensor(const Sht31Sensor&) = delete;
    Sht31Sensor & operator=(const Sht31Sensor &) = delete;
    ~Sht31Sensor();
    std::variant<Measurement, std::string> measure();
 private:
    /* Number of the i2c bus to use */
    int busNumber;
    std::string getDeviceName();
    // Closed in destructor as in RAII
    struct sht31_sensor sensorState;
    struct sht31_measurement sensorMeasurement;
};

#endif  // AGENT_ONLINE_TEMP_METRICS_INCLUDE_SENSOR_H_
