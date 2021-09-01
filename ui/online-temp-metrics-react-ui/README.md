# Online temp metrics React UI

Simple React app that fetches the temperature metrics data from a daemon running on the RPI. A Flask backend communicates with the React app using Websockets, and with the deamon using TPC sockets. Plot the data dynamically using plotly.
The original plan was to use gRPC streaming RPC to directly communicate a C++ daemon with the React app running on the browser, but Conan.io doesn't support ARM architectures, and building gRPC from source on RPI it's not trivial.

See [backend's README](./backend/README.md) for instructions for launching the app. 

## References

- [Easy WebSockets with Flask and Gevent](https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent)
- [Flask-SocketIO docs](https://flask-socketio.readthedocs.io/en/latest/index.html)
- [Getting Started with Typescript and Socket.Io](https://tutorialedge.net/typescript/typescript-socket-io-tutorial/)
- [socket.io docs](https://socket.io/docs/v3/client-initialization/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)