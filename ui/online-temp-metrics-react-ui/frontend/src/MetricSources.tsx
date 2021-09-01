import { io, Socket } from "socket.io-client";
import { setTimeout } from "timers";

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

interface WebsocketMetricsSourceError {
  code: number,
  message: string
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
  // static readonly ERROR_MESSAGE = 'metricsError';
  private readonly socket: Socket;
  private sink?: MetricsSink;
  constructor() {
    // by default this uses the same URL as the endpoint that served this React app
    // TODO error handling
    this.socket = io();
    this.setup_message_handling();
  }

  start(sourceProps: {[key: string]: string}, 
        sink: MetricsSink) {
    const hostname = sourceProps['hostname'];
    console.log(`Fetching data for hostname=[${hostname}]`);
    this.sink = sink;
    
    // TODO: error handling. Another message for errors I guess? This can easily lead to 
    // a state machine waiting for an ack from the server, and Erlang style communication
    this.socket.emit('metricsStart', {hostname: hostname});
    console.log(`Sent 'metricsStart' to backend for data ${JSON.stringify({hostname: hostname})}`);
  }

  stop() {
    return new Promise((resolve, reject) => {
      // TODO: error handling
      this.socket.emit('metricsStop');
      console.log(`Sent 'metricsStop' to backend`);      
      // Give some time to get an error message from backend
      setTimeout(() => {
        this.sink = undefined;
        console.log(`Closed sink`);
      }, 1000);       
      resolve(); // FIXME resolve in the timeout fun, if no errors yet (use state machien for that)
    }) as Promise<void>;
  }

  private log_message(msgName: string, msgPayload: any) {
    console.log(`Got '${msgName}' message from backend with payload ${JSON.stringify(msgPayload)}`);
  }

  /** This function should be called just once, or we'll process messages more than once */
  private setup_message_handling() {
    const log_message = this.log_message.bind(this);
    const self = this;
    this.socket.on('metricsError', function(msgPayload) {
      log_message('metricsError', msgPayload);
      const error = msgPayload as WebsocketMetricsSourceError;
      if (self.sink !== undefined) {
        self.sink.reportError(new Error(`Server error with code=[${error.code}] and message=[${error.message}]`));
      }
    });

    this.socket.on('metricsMeasurement', function(msgPayload) {
      log_message('metricsMeasurement', msgPayload);
      const measurement = msgPayload as WebsocketMetricsSourceMeasurement;
      if (self.sink !== undefined) {
        self.sink.pushDatum(new Date(measurement.timestamp), measurement.value);
      }
    });
  }
}
