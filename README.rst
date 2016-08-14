helium-python
===============

|build-status| |coverage-status| |code-climate| |docs|

A Python package for building applications with the Helium
API. Helium <https://www.helium.com/> is an integrated platform of
smart sensors, communication, edge-compute and API that enables
numerous sensing applications. For more information about the
underlying REST API, check out the Helium docs at <https://docs.helium.com/>

Installation
------------

Assuming you're using ``pip``, add this line to your ``setup.py``::

   requires = ['helium-python']

or to your ``requirements.txt`` file::

   helium-python


Usage
---------------

Please check out the library documentation at
<https://readthedocs.org/projects/helium-python/> for the latest
examples and complete reference.


Development
------------

In order to develop for helium-python you will need to install tox::

  pip install tox

Since helium-python supports at least Python 2.7 and 3.5 you will need
to have at least one of those installed on your development
machine. The build automation will test all required versions when
code is pushed to this repository.

Clone this repository and run::

  tox

This will install the required packages and run the tests for the library.

We also use `flake8` to ensure we catch Python version differences and
common pitfalls quicker. Please run::

  tox -e lint

before you commit code and try to remove as many warnings as you
can. Once we figure out how strict some of the documentation
requirements need to be we will be running lint as part of automation.

In order to develop documentation you can run::

  tox -e docs html

or to see your documentation changes live::

  tox -e docs livehtml


To make a release tag the repository with a valid semantic version
<https://semver.org> version and push tags. The build automation will
automatically build and push releases to PyPi
<https://pypi.python.org>


Contributing
------------

Bug reports and pull requests are welcome on GitHub at
<https://github.com/helium/helium-python>. This project is intended to
be a safe, welcoming space for collaboration, and contributors are
expected to adhere to the Contributor Covenant code of conduct
<http://contributor-covenant.org/>.

License
----------

The gem is available as open source under the terms of the MIT License
<http://opensource.org/licenses/MIT>.

.. |build-status| image:: https://travis-ci.org/helium/helium-python.svg?branch=master
   :target: https://travis-ci.org/helium/helium-python
   :alt: Build status
.. |coverage-status| image:: https://coveralls.io/repos/github/helium/helium-python/badge.svg?branch=master
   :target: https://coveralls.io/github/helium/helium-python?branch=master
   :alt: Test coverage percentage
.. |code-climate| image:: https://codeclimate.com/github/helium/helium-python/badges/gpa.svg
   :target: https://codeclimate.com/github/helium/helium-python
   :alt: Code Climate
.. |docs| image:: https://readthedocs.org/projects/helium-python/badge/?version=latest
   :target: http://helium-python.readthedocs.org/
   :alt: Documentation
