#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>

#include "sht31_sensor.h"

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
char crc8(const char *data, int len)
{
  const char POLYNOMIAL = 0x31;
  char crc = 0xFF;
  int j;
  int i;
  
  for (j = len; j; --j ) {
    crc ^= *data++;

    for ( i = 8; i; --i ) {
      crc = ( crc & 0x80 )
            ? (crc << 1) ^ POLYNOMIAL
            : (crc << 1);
    }
  }
  return crc;
}

int sht31_measure(struct sht31_measurement* measurement)
{
	// Create I2C bus
	int file;
	char *bus = "/dev/i2c-1";
	if((file = open(bus, O_RDWR)) < 0) 
	{
		printf("Failed to open the bus. \n");
		return 1;
	}
	// Get I2C device, SHT31 I2C address is 0x44(68)
	ioctl(file, I2C_SLAVE, 0x44);
 
	// Send high repeatability measurement command
	// Command msb, command lsb(0x2C, 0x06)
	char config[2] = {0};
	config[0] = 0x2C;
	config[1] = 0x06;
	if (write(file, config, 2) < 0) 
	{
		printf("Failed to send write command. \n");
		return 2;
	};
	sleep(1);
	// this is too fast and hangs the sensor after some measurements
	// usleep(64000); // microsecs

	// Read 6 bytes of data
	// temp msb, temp lsb, temp CRC, humidity msb, humidity lsb, humidity CRC
	char data[6] = {0};
	if(read(file, data, 6) != 6)
	{
		printf("Error : Input/output Error \n");
		close(file);
		return 3;
	}
	close(file);
	if ( data[2] != crc8(data, 2) || data[5] != crc8(data+3, 2)) 
	{
		printf("CRC check failure \n");
		return 4;
	}

	// Convert the data
	double cTemp = (((data[0] * 256) + data[1]) * 175.0) / 65535.0  - 45.0;
	// double fTemp = (((data[0] * 256) + data[1]) * 315.0) / 65535.0 - 49.0;
	double humidity = (((data[3] * 256) + data[4])) * 100.0 / 65535.0;
 
	
	measurement->humidity = humidity;
	measurement->temperature = cTemp;

	return 0;
}
