import React from 'react';
import './App.css';
import { Button, Divider, TextField, Typography } from '@material-ui/core';
import Plot from 'react-plotly.js';
import { MetricsSink, MetricsSource } from './MetricSources';

interface PlayMetricsButtonProps {
  measuring: boolean,
  onClick: () => void
}
interface PlayMetricsButtonState {}
/**
 * Button to start or stop the metrics collection
 * */
class PlayMetricsButton extends React.Component<PlayMetricsButtonProps, PlayMetricsButtonState> {
  constructor(props: PlayMetricsButtonProps) {
    super(props);

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    this.props.onClick();
  }

  render() {
    return (
      <div className="Basic-button">
        <Button onClick={this.handleClick} variant="contained" color="primary">{this.props.measuring ? "Stop" : "Start"}</Button>
      </div>
    );
  }
}

interface MetricsControlPanelProps {
  /** Size in data points of the sliding window we move
   * right as new data arrives */ 
  plotWindowSize?: number,
  /** We only keep in the plot the latest dataBufferSize received */
  dataBufferSize?: number
  /** Where we are getting the data from */
  metricsSource: MetricsSource
}
// Extending instead of nesting because react doesn't really
// support nested state properties https://stackoverflow.com/questions/43040721/how-to-update-nested-state-properties-in-react
interface MetricsControlPanelState extends MetricsPlotProps {
  agentHostname: string,
  measuring: boolean
}
class MetricsControlPanel extends React.Component<MetricsControlPanelProps, MetricsControlPanelState> 
                          implements MetricsSink {
  /** Default for props.plotWindowSize  */
  static readonly DEFAULT_PLOT_WINDOW_SIZE = 5;
  /** Default for props.dataBufferSize */
  static readonly DEFAULT_DATA_BUFFER_SIZE = 10;
  private static readonly WINDOW_PADDING_MILLIS = 50;

  private getPlotWindowSize(): number {
    return this.props?.plotWindowSize || MetricsControlPanel.DEFAULT_PLOT_WINDOW_SIZE;
  }

  private getDataBufferSize(): number {
    return this.props?.dataBufferSize || MetricsControlPanel.DEFAULT_DATA_BUFFER_SIZE;
  }

  constructor(props: MetricsControlPanelProps) {
    super(props);
    this.state = {
      agentHostname: "hostname",
      measuring: false,
      plotData: {
        x: [], y: [],
        mode: 'lines+markers',
        name: "temperature"
      }, 
      plotLayout: {
        datarevision: 0,
        margin: {
          t: 20, //top margin
          l: 20, //left margin
          r: 20, //right margin
          b: 20 //bottom margin
        },
        // We also need in the <Plot>:
        // - style={{width:"100%"}}  for the plot to resize to 100%
        // - useResizeHandler={true} for the plot to readjust when the window size changes
        autosize: true
      },
      plotRevision: 0
    };
    this.handleTextChange = this.handleTextChange.bind(this);
    this.handlePlayMetricsButtonClick = this.handlePlayMetricsButtonClick.bind(this);
    this.pushDatum = this.pushDatum.bind(this);
  }

  pushDatum(x: Date, y: Plotly.Datum) {
    const plotWindowSize = this.getPlotWindowSize();
    const dataBufferSize = this.getDataBufferSize();
    this.setState(function(state) {
      // add data
      const plotData = Object.assign({}, state.plotData);
      let xs = (plotData.x as Plotly.Datum[]).concat([x]);
      let ys = (plotData.y as Plotly.Datum[]).concat([y]);
      if (xs.length > dataBufferSize) {
         xs = xs.slice(1);
         ys = ys.slice(1);
      }
      plotData.x = xs;
      plotData.y = ys;

      const plotLayout = Object.assign({}, state.plotLayout);

      // follow the plot
      //   there is at least 1 element because we just added it
      const startDate = new Date(xs[Math.max(0, xs.length - plotWindowSize)] as Date);
      const endDate = new Date(xs[xs.length-1] as Date);
      startDate.setTime(startDate.getTime() - MetricsControlPanel.WINDOW_PADDING_MILLIS);
      endDate.setTime(endDate.getTime() + MetricsControlPanel.WINDOW_PADDING_MILLIS);
      plotLayout.xaxis = {
        range: [startDate, endDate]
      };

      // trigger update
      plotLayout.datarevision = state.plotRevision + 1;
      const plotRevision = state.plotRevision + 1;

      return { 
        plotData: plotData,
        plotLayout: plotLayout,
        plotRevision: plotRevision
      };
    });
  }

  reportError(error: Error) {
    alert(`Error fetching data: ${error}`);
    this.stopMeasuring();
  }

  private stopMeasuring() {
    this.props.metricsSource.stop();
    this.setState({
      measuring: false
    });
  }

  handleTextChange(event: React.ChangeEvent<HTMLInputElement>) {
    this.setState({agentHostname: event.target.value});
  }

  handlePlayMetricsButtonClick() {
    const trimmedHostname = this.state.agentHostname.trim();
    if (this.state.measuring) {
      console.log(`Stop measuring for host [${trimmedHostname}]`);
      this.props.metricsSource.stop();
    } else {
      console.log(`Start measuring for host [${trimmedHostname}]`);
      this.props.metricsSource.start(this);
    }
    this.setState(prevState => ({
      measuring: !prevState.measuring
    }));
  }

  render() {
    return (
      <div>
        <div className="MetricsControlPanel">
          <PlayMetricsButton 
              measuring={this.state.measuring} onClick={this.handlePlayMetricsButtonClick}/>
          <TextField value={this.state.agentHostname} 
              onChange={this.handleTextChange} disabled={this.state.measuring}/>
        </div>
        <div>
          <MetricsPlot
            plotData={this.state.plotData}
            plotLayout = {this.state.plotLayout}
            plotRevision = {this.state.plotRevision}
          />
        </div>
      </div>
    );
  }
}

interface MetricsPlotProps {
  plotData: Partial<Plotly.ScatterData>,
  plotLayout: Partial<Plotly.Layout>,
  plotRevision: number
}
interface MetricsPlotState {}
class MetricsPlot extends React.Component<MetricsPlotProps, MetricsPlotState> {
  render() {
    return (
      <Plot data={[this.props.plotData]}
            layout={this.props.plotLayout}
            revision={this.props.plotRevision}
            useResizeHandler={true}
            style={{width:"100%"}}
      />
    );
  }
}

interface AppProps extends MetricsControlPanelProps {}
interface AppState {}
class App extends React.Component<AppProps, AppState> {
  render() {
    return (
      <div className="App">
        <Typography variant="h2" component="h2">Temperature</Typography>
        <Divider/>
        <MetricsControlPanel 
          metricsSource={this.props.metricsSource}
          plotWindowSize={this.props.plotWindowSize}
          dataBufferSize={this.props.dataBufferSize}
          />
      </div>
    );
  }
}

export default App;
