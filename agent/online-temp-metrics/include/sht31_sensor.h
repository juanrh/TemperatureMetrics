// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE
#ifndef AGENT_ONLINE_TEMP_METRICS_INCLUDE_SHT31_SENSOR_H_
#define AGENT_ONLINE_TEMP_METRICS_INCLUDE_SHT31_SENSOR_H_

#define SHT31_STATUS_OK 0
#define SHT31_STATUS_OPEN_BUS_FAILURE 1
#define SHT31_STATUS_CLOSE_BUS_FAILURE 2
#define SHT31_STATUS_SEND_MEASURE_CMD_FAILURE 3
#define SHT31_STATUS_SEND_MEASURE_CMD_IO_ERROR 4
#define SHT31_STATUS_CRC_CHECK_FAILURE 5

struct sht31_measurement {
    // Celsius degrees
    double temperature;
    double humidity;
};

/** State required for getting measurements from the sensor */
struct sht31_sensor {
    int file;
};


/** Open the sensor
 * @param bus Name of the I2C bus device, e.g. /dev/i2c-1
 * @param sensor Sensor struct that is initialized by this function
 * 
 * @return STATUS_OPEN_BUS_FAILURE on failure, otherwise STATUS_OK
*/
int sht31_open(const char* bus, struct sht31_sensor* sensor);
int sht31_measure(const struct sht31_sensor* sensor,
                  struct sht31_measurement* measurement);
int sht31_close(const struct sht31_sensor* sensor);

#endif  // AGENT_ONLINE_TEMP_METRICS_INCLUDE_SHT31_SENSOR_H_
