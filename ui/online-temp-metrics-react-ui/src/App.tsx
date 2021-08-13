import React from 'react';
import './App.css';
import { Button, Divider, TextField, Typography } from '@material-ui/core';

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

interface MetricsControlPanelProps {}
interface MetricsControlPanelState {
  agentHostname: string,
  measuring: boolean
}
class MetricsControlPanel extends React.Component<MetricsControlPanelProps, MetricsControlPanelState> {
  constructor(props: MetricsControlPanelProps) {
    super(props);
    this.state = {
      agentHostname: "hostname",
      measuring: false
    };
    this.handleTextChange = this.handleTextChange.bind(this);
    this.handlePlayMetricsButtonClick = this.handlePlayMetricsButtonClick.bind(this);
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
  }

  render() {
    return (
      <div className="MetricsControlPanel">
         <PlayMetricsButton 
            measuring={this.state.measuring} onClick={this.handlePlayMetricsButtonClick}/>
         <TextField value={this.state.agentHostname} 
            onChange={this.handleTextChange} disabled={this.state.measuring}/>
      </div>
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
