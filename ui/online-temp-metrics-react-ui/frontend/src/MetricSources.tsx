
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
