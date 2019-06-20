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

Nise uses tox to standardize the environment used when running tests. Essentially, tox manages its own virtual environment and a copy of required dependencies to run tests. To ensure a clean tox environment run ::

    tox -r

This will rebuild the tox virtual env and then run all tests.

To run unit tests specifically::

    tox -e py36

To lint the code base ::

    tox -e lint

Usage
===========
nise is a command line tool. Currently only accepting a limited number of arguments:

- *--start-date MM-dd-YYYY* (not supplied, if using --static-report-file yaml)
- *--end-date MM-dd-YYYY* (optional, defaults to today and current hour)
- (--aws | --ocp) required provider type
- *--aws-s3-bucket-name bucket_name*  (optional, must include --aws-s3-report-name) Note: Use local directory path to populate a "local S3 bucket".
- *--aws-s3-report-name report_name*  (optional, must include --aws-s3-bucket-name)
- *--aws-s3-report-prefix prefix_name*  (optional)
- *--aws-finalize finalize_choice* (optional, choices: ['copy', 'overwrite'])
- *--ocp-cluster-id cluster-id* (required when providing ocp type)
- *--insights-upload UPLOAD_URL* (optional) Note: Use local directory path to populate a "local upload directory".
- *--static-report-file file_name* (optional) Note: Static report generation based on specified yaml file.  See example_aws[ocp]_static_data.yml for examples.

Note: If `--aws-s3-report-name` or `--aws-s3-report-prefix` are specified they should match what is configured in the AWS cost usage report settings.

Note: If `--aws-finalize` is used the *copy* choice will create a local copy of the data with a `-finalized` suffix and invoice id populated.
      If *overwrite* is used, the regular data file generated will have invoice id populated

Note: If `--insights-upload` is and pointing to a URL endpoint you must have INSIGHTS_USER and INSIGHTS_PASSWORD set in your environment.

Note: If `--static-report-file` is used start_date will default to first day of current month.  `start_date: last_month` will be first day of previous month.  `start_date: today` will start at the first hour of current day.  `end_date` can support relative days from the `start_date`. i.e `end_date: 2` is two days after start date.

Note: `--static-report-file` usage dates has a special `full_period` key value which will specify a usage for the entire `start_date - end_date` range.

Below is an example usage of ``nise`` for AWS data::

    nise --start-date 06-03-2018 --aws

    nise --start-date 06-20-2018 --aws --aws-s3-bucket-name testbucket --aws-s3-report-name cur

    nise --start-date 06-20-2018 --aws --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur

    nise --start-date 06-20-2018 --aws --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur --aws-s3-report-prefix my-prefix

    nise --start-date 06-20-2018 --aws --aws-finalize copy

    nise --aws --static-report-file aws_static_data.yml

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

Below is an example usage of ``nise`` for OCP data::

    nise --start-date 06-03-2018 --ocp --ocp-cluster-id test-001

    nise --start-date 06-03-2018 --ocp --ocp-cluster-id test-001 --insights-upload  https://cloud.redhat.com/api/ingress/v1/upload

    nise --start-date 06-03-2018 --ocp --ocp-cluster-id test-001 --insights-upload  /local/path/upload_dir

    nise --ocp --ocp-cluster-id my-cluster-id --static-report-file ocp_static_data.yml

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>.csv.

Below is an example usage of ``nise`` for OCP running on AWS data::

    # First ensure that the resource_id and dates in both AWS and OCP static report files match

    nise --aws --static-report-file aws_static_data.yml

    nise --ocp --ocp-cluster-id my-cluster-id --static-report-file ocp_static_data.yml

Generated AWS reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

Generated OCP reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>.csv.

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
