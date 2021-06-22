from setuptools import setup

import sys

major = sys.version_info[0]
minor = sys.version_info[1]
supported_python_versions = [(3,7)]
if (major, minor) not in supported_python_versions:
    sys.exit("Python version {}.{} is not in the list of supported versions {}".format(major, minor, supported_python_versions))

setup(name='tempd',
      version='0.1',
      description='Temperatura metrics daemon',
      author='Juan Rodriguez Hortala',
      author_email='juan.rodriguez.hortala@gmail.com',
      license='Apache 2.0',
      packages=['tempd'],
      install_requires = [
        'mypy', 'typing_extensions', 'pylint'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)