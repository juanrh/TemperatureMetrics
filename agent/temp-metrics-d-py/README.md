# temp-metrics-d-py

## Development environment

### Setup

Create a development environmetn and install the dependencies.

```bash
# Install pyenv prerequisites: https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites
# install pyenv
curl https://pyenv.run | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

pyenv update

# Using same python version as the RPI 3B+
pyenv install 3.7.3
pyenv shell 3.7.3

pip install virtualenv

# create virtualenv
python -m virtualenv .venv

# enter virtualenv
source .venv/bin/activate

# install this package __and all its required dependencies in the env__
# in developer mode (so it is updated when the code changes).
# Use this to REFRESH THE INSTALLATION TO INSTALL NEW DEPENDENCIES
pip install -e .

# exit virtualenv
deactivate
```

Also 

- Install VsCode extensions: ms-python.python,matangover.mypy. Open the directory of this file as the VsCode root.

### Development

Create a production configuration from the template `conf/conf.template.json`

See VsCode tasks in `.vscode/tasks.json`, and invoke tasks with `inv -l`.

TODO: 

- deploy script and VsCode task to deploy to RPI with arg for IP with default to my mDNS. Package as egg and transfer with SCP, and restart the agent, use fabric for that. 
  - config upstart
- logging