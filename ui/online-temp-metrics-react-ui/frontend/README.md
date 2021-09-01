# Online temp metrics React UI - frontend

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app) with the command:

```bash
npx create-react-app online-temp-metrics-react-ui --template typescript
```

Tested with __node 14__.

## Available Scripts

__TL;DR__:

```bash
# download dependencies: only needed when changing dependencies
npm install

# release build
CI=true npm test && CI=true npm run build

# run debug: at http://localhost:3000/
npm start

# run release (local): at http://localhost:5000/
serve -s build
```

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.
Logs emitted with `console.log` and friends are visible in the browser: e.g. with Chrome dev tools in the "Console" tab

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

To [run all tests non-interactively](https://create-react-app.dev/docs/running-tests/#on-ci-servers): `CI=true npm test`

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

- To [force linting](https://create-react-app.dev/docs/running-tests/#continuous-integration) during the build: `CI=true npm run build`
- To run the build artifacts, a [simple local setup](https://create-react-app.dev/docs/deployment/#static-server)
  - One time setup: `sudo npm install -g serve`
  - Launch app: `serve -s build` which runs the app at http://localhost:5000/

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.


See [What does this “react-scripts eject” command do?](https://stackoverflow.com/questions/48308936/what-does-this-react-scripts-eject-command-do) for more details. This basically removes `create-react-app` as build wrapper, and exposes the complexity it abstract, which is useful for advanced setups.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

## References

- Plotly
  - Plotly has [MIT license](https://plotly.com/python/is-plotly-free/) and can be used offline
  - [Plotly vs Chart.js](https://stackshare.io/stackups/js-chart-vs-plotly-js): Plotly has feature parity with matplotlib, it renders faster, and can be used from other languages like Python.
  - [React Plotly.js in JavaScript](https://plotly.com/javascript/react/)
  - [Create JavaScript Real-Time Chart with Plotly.js](https://redstapler.co/javascript-realtime-chart-plotly/). To "follow the plot" here instead of `Plotly.relayout` we can just update `this.state.plotLayout.xaxis` in our plot component, so react-plotly integration takes care of updating it.
  - [Plot.ly + React and dynamic data](https://medium.com/@jmmccota/plotly-react-and-dynamic-data-d40c7292dbfb). Bottom line, as seen in [Refreshing the Plot](https://github.com/plotly/react-plotly.js/blob/master/README.md#refreshing-the-plot) we have to update the `revision` prop and also the `layout.datarevision` or change the (javascript) identify of the data variable to force a refresh. E.g.

    ```ts
    interface FooProps {}
    interface FooState {
        data: Partial<Plotly.ScatterData>,
        layout: Partial<Plotly.Layout>,
        revision: number
    }

    class Foo extends React.Component<FooProps, FooState> {
        constructor(props: FooProps) {
            super(props);
            this.state = {
                data: {
                    x: [0, 1, 2],
                    y: [2, 0, 1],
                    mode: 'lines+markers',
                    name: "temperature"
                }, 
                layout: {
                    datarevision: 0,
                    margin: {
                        t: 20, //top margin
                        l: 20, //left margin
                        r: 20, //right margin
                        b: 20 //bottom margin
                    }
                },
                revision: 0
            }
            this.increaseGraphic = this.increaseGraphic.bind(this);
        }

        componentDidMount() {
            setInterval(this.increaseGraphic, 1000);
        } 

        increaseGraphic = () => {
            console.log("increaseGraphic");
            const data = this.state.data;

            (data.x as Plotly.Datum[]).push(this.state.revision+3);
            (data.y as Plotly.Datum[]).push(Math.random() * 10);
    
            this.setState({ revision: this.state.revision + 1 });
            this.state.layout.datarevision = this.state.revision + 1;
        }

        render() {
            return (
                <Plot data={[this.state.data]}
                      layout={this.state.layout}
                      revision={this.state.revision}
                />
            );
        }
    }
    ```

  - [How to use the layout.autosize?](https://github.com/plotly/react-plotly.js/issues/76)
  - [JavaScript heap out of memory error with the quickstart Plot example](https://github.com/plotly/react-plotly.js/issues/135): I fixed this by updating to Node.js v14.17.5.
- Js
  - [Concurrency model and the event loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/EventLoop): similar to Erlang's actor model, a single actor aka runtime corresponding to a [WindowOrWorkerGlobalScope](https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope) for the window processes messages/events from a queue, but without ever interrupting event handler, i.e. [cooperative scheduling](https://hamidreza-s.github.io/erlang/scheduling/real-time/preemptive/migration/2016/02/09/erlang-scheduler-details.html). An implicit Erlang's receive is running at all times, similarly to Akka, and that is called the "event loop". This means event handling can hang the UI which leads to the "a script is taking too long to run" similar to Android's ["Application Not Responding" (ANR) dialog](https://google-developer-training.github.io/android-developer-fundamentals-course-concepts-v2/unit-3-working-in-the-background/lesson-7-background-tasks/7-1-c-asynctask-and-asynctaskloader/7-1-c-asynctask-and-asynctaskloader.html). This works because IO libraries in js are async and delegate work to some native component that does the work, and immediately free the event loop. Also, we can launch a web worker which is another actor/runtime with its own message queue, running concurrently without blocking the window's event loop, that can comunicate with the window's runtime via messages.
  - [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise). Similar to Scala's promises but implicitly running using as execution context the event loop of the window or worker where the promise is defined. 
  - [async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
  - [Use Web Workers in Create React App without ejecting and TypeScript](https://dev.to/cchanxzy/use-web-workers-in-create-react-app-without-ejecting-and-typescript-2ap5)
 