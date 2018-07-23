===========
Nise README
===========
|license| |Build Status| |codecov| |Updates|

~~~~~
About
~~~~~

A tool for generating sample cost and usage data for testing purposes.

Getting Started
===============

This is a Python project developed using Python 3.6. Make sure you have at least this version installed.

Development
===========

To get started developing against Nise first clone a local copy of the git repository. ::

    git clone https://github.com/project-koku/nise

Developing inside a virtual environment is recommended. A Pipfile is provided. Pipenv is recommended for combining virtual environment (virtualenv) and dependency management (pip). To install pipenv, use pip ::

    pip3 install pipenv

Then project dependencies and a virtual environment can be created using ::

    pipenv install --dev

To activate the virtual environment run ::

    pipenv shell

To build the command line tool run ::

    python setup.py install


Testing and Linting
-------------------

Nise uses tox to standardize the environment used when running tests. Essentially, tox manages its own virtual environment and a copy of required dependencies to run tests. To ensure a clean tox environement run ::

    tox -r

This will rebuild the tox virtual env and then run all tests.

To run unit tests specifically::

    tox -e py36

To lint the code base ::

    tox -e lint

Usage
===========
nise is a command line tool. Currently only accepting a limited number of arguments:

- *--start-date MM-dd-YYYY*
- *--end-date MM-dd-YYYY* (optional, defaults to today and current hour)
- *--output-file file*
- *--s3-bucket-name bucket_name*  (optional, must include --s3-report-name) Note: Use local directory path to populate a "local S3 bucket".
- *--s3-report-name report_name*  (optional, must include --s3-bucket-name)

Below is an example usage of ``nise``::

    nise --start-date 06-03-2018 --output-file test.csv

    nise --start-date 06-20-2018 --output-file test.csv --s3-bucket-name testbucket --s3-report-name cur

    nise --start-date 06-20-2018 --output-file test.csv --s3-bucket-name /local/path/testbucket --s3-report-name cur

Contributing
=============

Please refer to Contributing_.

.. _Contributing: https://github.com/project-koku/nise/blob/master/CONTRIBUTING.rst

.. |license| image:: https://img.shields.io/github/license/project-koku/nise.svg
   :target: https://github.com/project-koku/nise/blob/master/LICENSE
.. |Build Status| image:: https://travis-ci.org/project-koku/nise.svg?branch=master
   :target: https://travis-ci.org/project-koku/nise
.. |codecov| image:: https://codecov.io/gh/project-koku/nise/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/project-koku/nise
.. |Updates| image:: https://pyup.io/repos/github/project-koku/nise/shield.svg?t=1524249231720
   :target: https://pyup.io/repos/github/project-koku/nise/
