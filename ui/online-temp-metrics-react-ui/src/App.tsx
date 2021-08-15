import React from 'react';
import './App.css';
import { Button, Divider, TextField, Typography } from '@material-ui/core';
import Plot from 'react-plotly.js';

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
  // size in data points of the sliding window we move
  // right as new data arrives
  plotWindowSize?: number
}
// Extending instead of nesting because react doesn't really
// support nested state properties https://stackoverflow.com/questions/43040721/how-to-update-nested-state-properties-in-react
interface MetricsControlPanelState extends MetricsPlotProps {
  agentHostname: string,
  measuring: boolean
}
class MetricsControlPanel extends React.Component<MetricsControlPanelProps, MetricsControlPanelState> {
  private static readonly WINDOW_PADDING_MILLIS = 50; 
  readonly plotWindowSize: number;
  constructor(props: MetricsControlPanelProps) {
    super(props);
    this.plotWindowSize = this.props?.plotWindowSize || 5 ;
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

  private pushDatum(x: Date, y: Plotly.Datum) {
    const plotWindowSize = this.plotWindowSize;
    this.setState(function(state) {
      // add data
      const plotData = Object.assign({}, state.plotData);
      const xs = ((plotData.x) as Plotly.Datum[]).concat([x]);
      const ys = (plotData.y as Plotly.Datum[]).concat([y]);
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

  handleTextChange(event: React.ChangeEvent<HTMLInputElement>) {
    this.setState({agentHostname: event.target.value});
  }

  handlePlayMetricsButtonClick() {
    const trimmedHostname = this.state.agentHostname.trim();
    if (this.state.measuring) {
      console.log(`Stop measuring for host [${trimmedHostname}]`);
      // TODO
    } else {
      console.log(`Start measuring for host [${trimmedHostname}]`);
      // TODO
    }
    this.setState(prevState => ({
      measuring: !prevState.measuring
    }));

    // FIXME
      // add a new point to the right with random y
    this.pushDatum(new Date(), Math.random() * 10);
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


// TODO 
// - Add updated dependency that __pushes__ updates: consider setInterval but think whether
// it is fully background/concurrent or not, we need RPC
// - Delete old data
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

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <Typography variant="h2" component="h2">Temperature</Typography>
        <Divider/>
        <MetricsControlPanel/>
      </div>
    );
  }
}

export default App;
