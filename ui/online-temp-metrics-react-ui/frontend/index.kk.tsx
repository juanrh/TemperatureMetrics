import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { FakeMetricsSource } from './MetricSources';

// import * as net from 'net';

// const HOST = 'temp-comedor';
// const PORT = 65432;

ReactDOM.render(
  <React.StrictMode>
    <App 
      metricsSource={new FakeMetricsSource()}
      plotWindowSize={30}
      dataBufferSize={100}
    />
  </React.StrictMode>,
  document.getElementById('root')
);

// // FIXME
// console.log('Connecting to server ' + HOST +':'+ PORT);
// var client = new net.Socket();
// client.connect(PORT, HOST, function() {
//   console.log('CONNECTED TO: ' + HOST + ':' + PORT);
//   // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client
//  client.write('I am Chuck Norris!');

// });

// // Add a 'data' event handler for the client socket
// // data is what the server sent to this socket
// client.on('data', function(data) {
//   console.log('DATA: ' + data);
//   // Close the client socket completely
//   client.destroy();
// });

// // Add a 'close' event handler for the client socket
// client.on('close', function() {
//   console.log('Connection closed');
// });

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
