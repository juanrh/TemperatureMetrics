import { io, Socket } from "socket.io-client";

export interface MetricsSink {
    pushDatum(x: Date, y: Plotly.Datum): void;
    reportError(error: Error): void;
  }

export interface MetricsSource {
    /** The source can use `sink.reportError` to report issues at any time */
    start(sourceProps: {[key: string]: string},
          sink: MetricsSink): void
    /** Use the promise to report a failure shutting down */
    stop(): Promise<void>
  }

export interface FakeMetricsSourceProps {
    failOnStart?: boolean,
    failOnStop?: boolean
}
export class FakeMetricsSource implements MetricsSource {
  private scheduledTask?: NodeJS.Timeout;
  private readonly failOnStart: boolean;
  private readonly failOnStop: boolean;

  constructor(props: FakeMetricsSourceProps = {}) {
      this.failOnStart = props.failOnStart || false;
      this.failOnStop = props.failOnStop || false;
  }

  start(sourceProps: {[key: string]: string}, 
        sink: MetricsSink) {
    const hostname = sourceProps['hostname'];
    console.log(`Fetching data for hostname=[${hostname}]`);
    const failOnStart = this.failOnStart;
    this.scheduledTask = setInterval(function() {
      // add a new point to the right with random y
      sink.pushDatum(new Date(), Math.random() * 10);
      if (failOnStart) {
          sink.reportError(new Error("forced error on start"));
      }
    }, 50);
  }

  stop() {
    if (this.scheduledTask) {
      clearInterval(this.scheduledTask);
      this.scheduledTask = undefined;
    }
    return new Promise((resolve, reject) => {
        if (this.failOnStop) {
            console.log("rejecting");
            reject(new Error("forced error on stop"));
        } else {
            resolve();
        }
    }) as Promise<void>;
  }
}

interface WebsocketMetricsSourceMeasurement {
  timestamp: number,
  // temperature measurement
  value: number
}

/** A MetricsSource that gets the metrics from a websocket open
 * against the same backend endpoint that serves this React app.
 * 
 * Expects a property 'hostname' in sourceProps passed to `start`,
 * with the hostname of the agent that records the metrics. The backend
 * has the responsibility to connect to that host, and forward the
 * metrics to this metric source through the websocket
 */
export class WebsocketMetricsSource implements MetricsSource {
  private readonly socket: Socket;
  constructor() {
    // by default this uses the same URL as the endpoint that served this React app
    // TODO error handling
    this.socket = io();
  }

  start(sourceProps: {[key: string]: string}, 
        sink: MetricsSink) {
    const hostname = sourceProps['hostname'];
    console.log(`Fetching data for hostname=[${hostname}]`);
    
    // TODO: error handling. Another message for errors I guess? This can easily lead to 
    // a state machine waiting for an ack from the server, and Erlang style communication
    this.socket.emit('metricsStart', {hostname: hostname});
    console.log(`Sent 'metricsStart' to backend for data ${JSON.stringify({hostname: hostname})}`);
    this.socket.on('metricsMeasurement', function(msg) {
      console.log(`Got 'metricsMeasurement' from backend with data ${JSON.stringify(msg)}`);
      const measurement = msg as WebsocketMetricsSourceMeasurement;
      sink.pushDatum(new Date(measurement.timestamp), measurement.value);
    });
  }

  stop() {
    return new Promise((resolve, reject) => {
      // TODO: error handling
      this.socket.emit('metricsStop');
      console.log(`Sent 'metricsStop' to backend`);
      resolve();
    }) as Promise<void>;
  }
}
