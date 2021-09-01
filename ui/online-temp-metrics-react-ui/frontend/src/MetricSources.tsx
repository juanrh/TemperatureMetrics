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
  private static readonly STOP_TIMEOUT_MILLIS = 1000;
  private static readonly START_TIMEOUT_MILLIS = 1000;

  private readonly socket: Socket;
  private sink?: MetricsSink;
  /** We use this for a simple promise-like mechanism, as we don't have ask pattern
   * or become like in Akka, and we don't have call and we cannot change the receive
   * like in Erlang, and instead we have a fixed receive defined by the calls 
   * to `this.socket.on` we do in `setup_message_handling`. The idea is that when we
   * want to check if we get a response message we set `error` to an error and issue
   * a timer to fail with `sink.reportError` if error is still defined on timeout. For
   * this to work other receives set error to undefined on suitable receives. This is
   * quite limited as it cannot wait for several messages, but it is enough for this
   * simple protocol, and avoids complex state machine handling.
   * We have 2 synchronous calls to make to the backend, 'metricsStart' and 'metricsStop',
   * so we use 2 separate "error" variables to avoid mixing their results, which might
   * happen if the user starts and then stops very quickly
   */
  private startError?: Error;
  private stopError?: Error;
  constructor() {
    // by default this uses the same URL as the endpoint that served this React app
    this.socket = io();
    this.setup_message_handling();
  }

  start(sourceProps: {[key: string]: string}, 
        sink: MetricsSink) {
    const hostname = sourceProps['hostname'];
    console.log(`Fetching data for hostname=[${hostname}]`);
    this.sink = sink;
    
    this.socket.emit('metricsStart', {hostname: hostname});
    this.startError = new Error('Server timeout waiting for metric collection to start');
    const self = this;
    setTimeout(function(){
      if (self.startError !== undefined) {
        self.sink?.reportError(self.startError);
      }
    }, WebsocketMetricsSource.START_TIMEOUT_MILLIS);
    console.log(`Sent 'metricsStart' to backend for data ${JSON.stringify({hostname: hostname})}`);
  }

  stop() {
    return new Promise((resolve, reject) => {
      this.socket.emit('metricsStop');
      console.log(`Sent 'metricsStop' to backend`);
      this.stopError = new Error('Server timeout waiting for metric collection to stop');   
      // Give some time to get an error message from backend
      setTimeout(() => {
        this.sink = undefined;
        console.log(`Closed sink`);
        if (this.stopError !== undefined) {
          console.log(`Error stopping metrics`)
          reject(this.stopError)
        } else {
          resolve();
        }
      }, WebsocketMetricsSource.STOP_TIMEOUT_MILLIS);       
       
    }) as Promise<void>;
  }

  private log_message(msgName: string, msgPayload: any={}) {
    console.log(`Got '${msgName}' message from backend with payload ${JSON.stringify(msgPayload)}`);
  }


  /** This function should be called just once, or we'll process messages more than once */
  private setup_message_handling() {
    const self = this;

    this.socket.on('metricsError', function(msgPayload) {
      self.log_message('metricsError', msgPayload);
      self.startError = undefined; // to avoid double error reporting
      self.stopError = undefined; // to avoid double error reporting
      const error = msgPayload as WebsocketMetricsSourceError;
      if (self.sink !== undefined) {
        self.sink.reportError(new Error(`Server error with code=[${error.code}] and message=[${error.message}]`));
      }
    });

    this.socket.on('metricsStartOk', function(){
      self.log_message('metricsStartOk');
      self.startError = undefined;
    });

    this.socket.on('metricsStopOk', function(){
      self.log_message('metricsStopOk');
      self.stopError = undefined;
    });

    this.socket.on('metricsMeasurement', function(msgPayload) {
      self.log_message('metricsMeasurement', msgPayload);
      // Not necessary as Websocket messages cannot arrive out of order, so
      // we shouldn't receive a measurement before 'metricsStartOk'
      // self.startError = undefined;  
      const measurement = msgPayload as WebsocketMetricsSourceMeasurement;
      if (self.sink !== undefined) {
        self.sink.pushDatum(new Date(measurement.timestamp), measurement.value);
      }
    });
  }
}
