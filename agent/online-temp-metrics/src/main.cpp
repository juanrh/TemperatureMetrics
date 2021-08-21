#include <iostream>

extern "C" {
	#include "sht31_sensor.h"
}


int main(int argc, char *argv[])
{
    std::cout << "hello word!\n";

	struct sht31_measurement measurement = {0, -1};
	if (int mesurement_error_code = sht31_measure(& measurement) != 0) {
		std::cout << "Measurement error, error code=[" 
				  << mesurement_error_code << "]\n";
		return mesurement_error_code;
	};
	// struct sht31_measurement measurement = sht31_measure();
	printf("temperature=%4.2f, humidity=%4.2f\n", measurement.temperature, measurement.humidity);

    std::cout << "bye!" << std::endl;
    return 0;
}