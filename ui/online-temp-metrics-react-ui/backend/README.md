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

# Install a recent python version
pyenv install 3.9.7
pyenv shell 3.9.7

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

### Launching the app

The frontend should be served by the front, the instructions in [frontend's README](../frontend/README.md) only apply for front end development

```bash
$ inv -l
Available tasks:

  run   Launch web app to default port at http://127.0.0.1:5000/index.html
```