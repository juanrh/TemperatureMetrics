#ifndef SHT31_SENSOR_H_
#define SHT31_SENSOR_H_

// struct sht31_measurement ;

struct sht31_measurement 
{
    // Celsius degrees
    double temperature;
    // pass -1 to indicate a wrong measurement
    double humidity;
};

int sht31_measure(struct sht31_measurement* measurement);

#endif