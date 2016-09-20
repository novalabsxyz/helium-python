# helium-python


[![Build Status](https://travis-ci.org/helium/helium-python.svg?branch=master)](https://travis-ci.org/helium/helium-python)
[![Build status](https://ci.appveyor.com/api/projects/status/qrfieklw1yph7lkg?svg=true)](https://ci.appveyor.com/project/madninja/helium-python)
[![Coverage Status](https://coveralls.io/repos/github/helium/helium-python/badge.svg?branch=master)](https://coveralls.io/github/helium/helium-python?branch=master)
[![Code Climate](https://codeclimate.com/github/helium/helium-python/badges/gpa.svg)](https://codeclimate.com/github/helium/helium-python)
[![Docs](https://readthedocs.org/projects/helium-python/badge/?version=latest)](http://helium-python.readthedocs.org/)

`helium-python` is a Python package for building applications with the
Helium API. [Helium](https://www.helium.com) is an integrated platform
of smart sensors, communication, edge-compute and API that enables
numerous sensing applications. For more information about the
underlying REST API, check out the complete
[Helium documentation](https://docs.helium.com).

## Installation

Assuming you're using `pip`, add this line to your `setup.py`:

```
requires = ['helium-python']
```

or to your `requirements.txt` file:

```
helium-python
```

## Usage and Documentation


Please check out the
[helium-python documentation on Read the Docs](https://readthedocs.org/projects/helium-python)
for the latest examples and complete reference.


## Development


In order to develop for helium-python you will need to install tox:

```
pip install tox
```

Since `helium-python` supports at least Python 2.7 and 3.5 you will
need to have at least one of those installed on your development
machine. The build automation will test all required versions when
code is pushed to this repository.

Clone this repository and run:

```
$ tox
```

This will install the required packages and run the tests for the
library. Installing `tox` removes the need to install or use
`virtualenv` since tox manages virtual environments already.

By default the tests will replay back previously recorded API
interactions. To affect how tests interact with the Helium API you
will have to

* Set a `HELIUM_API_KEY` environment variable to a valid Helium API key. For example in `bash`:


```
$ export HELIUM_API_KEY=<my api key>
```

* Set `HELIUM_RECORD_MODE` to one of:

* **none** - (default) Only play back recorded API interactions.

* **once** - Only record interactions for which no recording exist. If
  you get an error message from betamax complaining about a recording
  not matching an interaction that means that your test has new API
  interactions with it. Remove the cassette referred to in the error
  message and run the test again to re-generate it .

We use `flake8` to ensure we catch Python version differences and
common pitfalls quicker. Please run:

```
$ tox -e lint
```

before you commit code and try to remove as many warnings as you
can. Once we figure out how strict some of the documentation
requirements need to be we will be running lint as part of automation.

In order to develop documentation you can run::

```
$ tox -e docs html
```

or to see your documentation changes live:

```
$ tox -e docs livehtml
```

To make a release tag the repository with a valid
[semantic version](https://semver.org) version and push tags. The
build automation will automatically build and push releases to
[PyPi](https://pypi.python.org).

##  Helium Documentation and Community Support

* **Docs** - Complete documenation for all parts of Helium can be
  found at [docs.helium.com](https://docs/helium.com).

* **chat.helium.com** - If you have questions or ideas about how to
  use this code - or any part of Helium - head over the
  [chat.helium.com](https://chat.helium.com). We're standing by to
  help.
