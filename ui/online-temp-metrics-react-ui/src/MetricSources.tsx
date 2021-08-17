
export interface MetricsSink {
    pushDatum(x: Date, y: Plotly.Datum): void;
    reportError(error: Error): void;
  }

export interface MetricsSource {
    /** The source can use `sink.reportError` to report issues at any time */
    start(sink: MetricsSink): void
    /** Use the promise to report a failure shutting down */
    stop(): Promise<'ok'>
  }
  
export class FakeMetricsSource implements MetricsSource {
  private scheduledTask?: NodeJS.Timeout;

  start(sink: MetricsSink) {
    this.scheduledTask = setInterval(function() {
      // add a new point to the right with random y
      sink.pushDatum(new Date(), Math.random() * 10);
    }, 50);
  }

  stop() {
    if (this.scheduledTask) {
      clearInterval(this.scheduledTask);
      this.scheduledTask = undefined;
    }
    return new Promise((resolve, reject) => {
      resolve('ok');
    }) as Promise<'ok'>;
  }
}
