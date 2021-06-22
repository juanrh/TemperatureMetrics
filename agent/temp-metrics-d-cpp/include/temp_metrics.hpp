#include <ctime>
#include <memory>

#ifndef TEMP_METRICS_H
#define TEMP_METRICS_H

struct TempMeasurement {
    std::time_t timestamp;
    float temp;
    float humidity;
};

template<typename Measurement>
class Sensor {
    virtual ~Sensor();
    /** Only valid measurements should be returned, e.g. discard NaN returned by the driver 
     * and retry until a valid measurement is obtained*/
    virtual Measurement measure();
};

template<typename Measurement>
class Sink {
    virtual ~Sink();
    virtual void publish(std::shared_ptr<Measurement> measurement);
};

#endif