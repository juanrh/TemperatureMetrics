#include <ctime>
#include <memory>

#ifndef TEMP_METRICS_H
#define TEMP_METRICS_H

struct TempMeasurement {
    std::time_t timestamp;
    int temp;
};

template<class Measurement>
class Sensor {
    virtual ~Sensor();
    virtual Measurement measure();
};

template<class Measurement>
class Sink {
    virtual void publish(std::shared_ptr<Measurement> measurement);
};

#endif