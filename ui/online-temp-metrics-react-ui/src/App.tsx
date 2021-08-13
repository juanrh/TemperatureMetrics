import React from 'react';
import './App.css';

interface PlayMetricsButtonProps {}
interface PlayMetricsButtonState {
  measuring: boolean
}
/**
 * Button to start or stop the metrics collection
 * */
class PlayMetricsButton extends React.Component<PlayMetricsButtonProps, PlayMetricsButtonState> {
  constructor(props: PlayMetricsButtonProps) {
    super(props);
    this.state = {
      measuring: false
    }
    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    if (this.state.measuring) {
      console.log("Stop measuring");
    } else {
      console.log("Start measuring");
    }
    this.setState(prevState => ({
      measuring: !prevState.measuring
    }));
  }

  render() {
    return (
      <button onClick={this.handleClick}>{this.state.measuring ? "Stop" : "Start"}</button>
    );
  }
}

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <h2 className="Basic-text">Temperature</h2>
        <hr/>
          <PlayMetricsButton/>
      </div>
    );
  }
}

export default App;

/**

TODO add text input to enter server address:

- add a parent component with children PlayMetricsButton and a text input. Use flex to render right

<div style={{display: 'flex',  justifyContent:'left', alignItems: 'left'}}>

- lift the state to that parent component, as the button needs the text input to run

*/