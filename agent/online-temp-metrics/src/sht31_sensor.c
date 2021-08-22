// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE
#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>

#include "./sht31_sensor.h"

/**
 * Code based on http://www.getmicros.net/raspberry-pi-and-sht31-sensor-example-in-c.php.
 *
 * To get info about I2C devices
 * 
 * ```
 * i2cdetect -l
 * i2cdetect -y 1
 * ```
 * 
 * If you measure too fast it ends up hanging the bus. 1 second sleep time works fine.
 * Bus can be reset by phisically disconnecting and connecting the sensor, this has happened
 * to other people too, see e.g. https://tlfong01.blog/2021/01/12/i2c-bus-fails-after-a-few-sensor-reads/,
 * where is says that shorter cables can help.  
 * This looks like a hardware limitation. 
*/

/*
* Code from https://github.com/sfeakes/Adafruit-sht31-for-PI/blob/master/sht31-d.c
* 
* CRC-8 formula from page 14 of SHT spec pdf
*
* Test data 0xBE, 0xEF should yield 0x92
*
* Initialization data 0xFF
* Polynomial 0x31 (x8 + x5 +x4 +1)
* Final XOR 0x00
*/

static const char CRC_POLYNOMIAL = 0x31;
char sht31_crc(const char *data, int len) {
  char crc = 0xFF;
  int j;
  int i;

  for (j = len; j; --j) {
    crc ^= *data++;

    for (i = 8; i; --i) {
      crc = (crc & 0x80)
            ? (crc << 1) ^ CRC_POLYNOMIAL
            : (crc << 1);
    }
  }
  return crc;
}

static const char SENSOR_ADDRESS = 0x44;
#define SEND_MEASURE_CMD_SIZE 2
#define MEASURE_MSG_BYTE_SIZE 6
// High repeatability measurement command
// Command msb, command lsb(0x2C, 0x06)
// msb = most significant byte, lsb = least significant byte
static const char SEND_MEASURE_CMD_CONFIG[SEND_MEASURE_CMD_SIZE] = {
    // command most significant byte
    0x2C,
    // command least significant byte
    0x06
};
// this is too fast and hangs the sensor after some measurements
// usleep(64000); // microsecs
static const unsigned int MEASUREMENT_SLEEP_TIME_SECS = 1;

int sht31_open(const char* bus, struct sht31_sensor* sensor) {
    // Create I2C bus
    int file;

    if ((file = open(bus, O_RDWR)) < 0) {
        return SHT31_STATUS_OPEN_BUS_FAILURE;
    }
    ioctl(file, I2C_SLAVE, SENSOR_ADDRESS);

    sensor->file = file;

    return SHT31_STATUS_OK;
}

int sht31_measure(const struct sht31_sensor* sensor,
                  struct sht31_measurement* measurement) {
    if (write(sensor->file, SEND_MEASURE_CMD_CONFIG, SEND_MEASURE_CMD_SIZE) < 0) {
        return SHT31_STATUS_SEND_MEASURE_CMD_FAILURE;
    }
    sleep(MEASUREMENT_SLEEP_TIME_SECS);

    // Read 6 bytes of data
    // temp msb, temp lsb, temp CRC, humidity msb, humidity lsb, humidity CRC
    char data[MEASURE_MSG_BYTE_SIZE] = {0};
    if (read(sensor->file, data, MEASURE_MSG_BYTE_SIZE) != MEASURE_MSG_BYTE_SIZE) {
        return SHT31_STATUS_SEND_MEASURE_CMD_IO_ERROR;
    }
    if (data[2] != sht31_crc(data, 2) || data[5] != sht31_crc(data+3, 2)) {
        return SHT31_STATUS_CRC_CHECK_FAILURE;
    }

    // Convert the data
    double cTemp = (((data[0] * 256) + data[1]) * 175.0) / 65535.0  - 45.0;
    double humidity = (((data[3] * 256) + data[4])) * 100.0 / 65535.0;
    measurement->temperature = cTemp;
    measurement->humidity = humidity;

    return SHT31_STATUS_OK;
}

int sht31_close(const struct sht31_sensor* sensor) {
    int close_status = close(sensor->file);
    if (close_status != 0) {
        return SHT31_STATUS_CLOSE_BUS_FAILURE;
    }
    return SHT31_STATUS_OK;
}
