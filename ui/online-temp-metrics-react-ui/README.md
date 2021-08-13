# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app) with the command:

```bash
npx create-react-app online-temp-metrics-react-ui --template typescript
```

## Available Scripts

__TL;DR__:

```bash
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
