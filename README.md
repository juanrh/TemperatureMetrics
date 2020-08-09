# TemperatureMetrics

## References

- [rusoto](https://github.com/rusoto/rusoto)
- [tokio](https://tokio.rs/tokio/tutorial)
- CDK
  - [CDK Developer Guide](https://docs.aws.amazon.com/cdk/latest/guide/home.html)

## Design

A daemon running on a SBC with a temperature sensor sends temperature metrics to CloudWatch at a regular cadence.

- To CW Metrics: so we can easily plot in a CW dashboard
- To CW logs: same metrics in JSON format in case we eventually want to export them for further analysis or longer retention

Why not using existing tools like Fluentd o Logstash/Filebeat + Elasticsearch, or more high level libraries?? For two reasons:

- The main goal of this project is learning about embedded development in Rust
- As a result, we want a simple setup, with the fewest moving parts, that we can deploy very easily

### Hardware

RPI 3B+ with GrovePi+ and Grove temperature and humidity sensor
