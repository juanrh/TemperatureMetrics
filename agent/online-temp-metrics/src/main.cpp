// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE
#include <iostream>

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
    struct sht31_sensor sensor;
    failIfNotOk(sht31_open("/dev/i2c-1", & sensor),
                std::string("Failed to open the I2C bus"));

    struct sht31_measurement measurement;
    for (int i=0; i < 3; i++) {
        int mesurement_error_code = sht31_measure(& sensor, & measurement);
        switch (mesurement_error_code) {
        case SHT31_STATUS_OK:
            printf("temperature=%4.2f, humidity=%4.2f\n",
                   measurement.temperature, measurement.humidity);
            break;
        case SHT31_STATUS_OPEN_BUS_FAILURE:
            failWithMsg(mesurement_error_code, std::string("Failure opening I2C bus"));
            break;
        case SHT31_STATUS_CLOSE_BUS_FAILURE:
            failWithMsg(mesurement_error_code, std::string("Failure closing I2C bus"));
            break;
        case SHT31_STATUS_SEND_MEASURE_CMD_FAILURE:
            failWithMsg(mesurement_error_code, std::string("Failure sending sensor measure command"));
            break;
        case SHT31_STATUS_SEND_MEASURE_CMD_IO_ERROR:
            failWithMsg(mesurement_error_code, std::string("IOError reading measure command result"));
            break;
        case SHT31_STATUS_CRC_CHECK_FAILURE:
            failWithMsg(mesurement_error_code,
                        std::string("CRC check failure for read sensormeasurement"));
            break;
        default:
            break;
        }
    }

    // FIXME: use RAII in C++ sensor wrapper class
    sht31_close(& sensor);

    return 0;
}
