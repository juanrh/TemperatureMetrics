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
## For Ubuntu 22.04 use `CC=gcc-10 pyenv install 3.7.3` https://stackoverflow.com/questions/73239153/pyenv-giving-errors-after-trying-to-install-python-3-6-9
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

Create a production configuration from the template `conf/conf.template.json`. Same for the AWS credentials, starting with `conf/aws_credentials.template.sh`. Regarding the condiguration: 

- "logging" section specifies parameters for [`TimedRotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler), with "rotationInterval" equal to "interval", "rotationIntervalUnit" equal to "when", and "maxLogFiles" equal to "backupCount"
- "aws" specifies which credentials filename to use. For devel it's useful to use `aws_credentials.template.sh` so we don't actually call CloudWatch (cost, handling many AWS accounts, ...). When credentials are empty strings a fake cloudwatch client is used, that just logs the calls to `put_metric_data` it receives.

See VsCode tasks in `.vscode/tasks.json`, and invoke tasks with `inv -l`:

```bash
# run unit tests, linter, and other code quality tools
inv release

# Run locally with fake cloudwatch metrics client
inv launch-agent --conf=.local/dev.json
# Check Prometheus metrics
curl localhost:8000/metrics | grep tempd

# deploy to prod
inv deploy --conf=.local/comedor.json

# check agent status in prod
inv check-agent-status --conf=.local/comedor.json
```
