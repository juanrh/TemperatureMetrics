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

  private pushDatum(x: Plotly.Datum, y: Plotly.Datum) {
    const data = this.state.plotData;
    (data.x as Plotly.Datum[]).push(x);
    (data.y as Plotly.Datum[]).push(y);
    this.setState(function (state) {
      const plotLayout = state.plotLayout;
      plotLayout.datarevision = state.plotRevision + 1;
      return { 
        plotRevision: state.plotRevision + 1,
        plotLayout: plotLayout
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
    this.pushDatum(this.state.plotRevision, Math.random() * 10);
      // follow the plot
    const plotWindowSize = this.plotWindowSize;
    this.setState(function (state) {
      const plotLayout = state.plotLayout;
      if (state.plotData.x?.length || 0 > plotWindowSize) { 
        plotLayout.xaxis = {
          range: [state.plotRevision - plotWindowSize, state.plotRevision]
        }
      }
      return {
        plotLayout: plotLayout
      };
    });
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
// - Plot with date as x: note `export type Datum = string | number | Date | null;` so it
// might be trivial
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
