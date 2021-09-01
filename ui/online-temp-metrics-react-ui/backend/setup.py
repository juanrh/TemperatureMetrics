from setuptools import setup

import sys

major = sys.version_info[0]
minor = sys.version_info[1]
supported_python_versions = [(3,9)]
if (major, minor) not in supported_python_versions:
    sys.exit("Python version {}.{} is not in the list of supported versions {}".format(major, minor, supported_python_versions))

setup(name='tempd',
      version='0.1',
      description='Online temperature metrics web app',
      author='Juan Rodriguez Hortala',
      author_email='juan.rodriguez.hortala@gmail.com',
      license='Apache 2.0',
      # skip packaging tests
      packages=['metricsapp'],
      install_requires = [
        'pip', 'wheel', 'setuptools', 'pytest', 'pytest-cov',
        'mypy>=0.910', 'typing_extensions>=3.10.0.0', 'pylint>=2.8.3',
        'invoke>=1.5.0', 'fabric>=2.6.0',
        'Flask>=2.0.1', 'Flask-SocketIO>=5.1.1', 'simple-websocket>=0.3.0'
      ],
      zip_safe=False)