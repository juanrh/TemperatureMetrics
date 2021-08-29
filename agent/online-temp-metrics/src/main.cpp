// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE
#include <iostream>
#include "./sensors.h"

extern "C" {
    #include "sht31_sensor.h"
}

void failWithMsg(int status_code, const std::string & msg) {
    std::cout << msg << ", error code=["
              << status_code<< "]\n";
    exit(status_code);
}

void failIfNotOk(int status_code, const std::string & msg) {
    if (status_code != SHT31_STATUS_OK) {
        failWithMsg(status_code, msg);
    }
}

int main(int argc, char *argv[]) {
    Sht31Sensor sensor{1};

    for (int i=0; i < 3; i++) {
        auto measurementOpt = sensor.measure();
        Measurement* measurement = std::get_if<Measurement>(& measurementOpt);
        if  (measurement != nullptr) {
            std::cout << "Measurement: " << *measurement << "\n";
        } else {
            std::string errorMsg = std::get<std::string>(measurementOpt);
            std::cout << "Measurement error: " << errorMsg << "\n";
        }
    }

    return 0;
}
