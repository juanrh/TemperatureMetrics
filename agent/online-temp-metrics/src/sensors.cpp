// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE

#include "./sensors.h"

std::ostream& operator<<(std::ostream& os, const Measurement& measurement) {
    os << std::fixed << std::setprecision(3)
       << std::setw(4) << "temperature: [" << measurement.temperature << "], "
       << std::setw(4) << "humidity: [" << measurement.humidity << "]";
    return os;
}


Sht31Sensor::Sht31Sensor(int busNumber): busNumber(busNumber) {
    std::string i2cDeviceName = this->getDeviceName();
    // FIXME: logging instead
    std::cout << "Using i2c device=[" << i2cDeviceName << "]\n";
    sht31_open(i2cDeviceName.c_str(), & this->sensorState);
}

Sht31Sensor::~Sht31Sensor() {
    // FIXME: logging instead
    std::cout << "Closing device [" << this->getDeviceName() << "]\n";
    sht31_close(& this->sensorState);
}

std::string Sht31Sensor::getDeviceName() {
    std::ostringstream i2cDeviceNameStream;
    i2cDeviceNameStream << "/dev/i2c-" << busNumber;
    return i2cDeviceNameStream.str();
}

std::variant<Measurement, std::string> Sht31Sensor::measure() {
    int mesurementErrorCode = sht31_measure(& this->sensorState, & sensorMeasurement);
    // If we define measurement in the switch then we get "crosses initialization" errors as its scope
    // it's not clear. Create it in an if scope, and only if we need to
    if (mesurementErrorCode == SHT31_STATUS_OK) {
        Measurement measurement = Measurement{
            this->sensorMeasurement.temperature,
            this->sensorMeasurement.humidity
        };
        // FIXME: logging instead
        std::cout << "got measurement " << measurement << "\n";
        return measurement;
    }
    switch (mesurementErrorCode) {
        case SHT31_STATUS_OPEN_BUS_FAILURE:
            return std::string("Failure opening I2C bus");
            break;
        case SHT31_STATUS_CLOSE_BUS_FAILURE:
            return std::string("Failure closing I2C bus");
            break;
        case SHT31_STATUS_SEND_MEASURE_CMD_FAILURE:
            return std::string("Failure sending sensor measure command");
            break;
        case SHT31_STATUS_SEND_MEASURE_CMD_IO_ERROR:
            return std::string("IOError reading measure command result");
            break;
        case SHT31_STATUS_CRC_CHECK_FAILURE:
            return std::string("CRC check failure for read sensormeasurement");
            break;
        default:
            return std::string{"Unknown error"};
    }
}
