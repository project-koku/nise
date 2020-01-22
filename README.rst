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


Publishing
__________

Please remember to sync your updated dependecies to setup.py with ::

    pipenv-setup sync -p

After that, make sure to increment the version in setup.py. As soon as your PR is merged to master, a new koku-nise package will built, tagged, and deployed to PyPI.

Prereqs
===========

- AWS population requires prior setup of AWS Cost and Usage Report of same name to be created, as well as associated Bucket, Policy, Role, etc.

Usage
===========
nise is a command line tool. Currently only accepting a limited number of arguments:

- *--start-date YYYY-MM-dd* (not supplied, if using --static-report-file yaml)
- *--end-date YYYY-MM-dd* (optional, defaults to today and current hour)
- (--aws | --ocp | --gcp | --azure) required provider type
- *--aws-s3-bucket-name bucket_name*  (optional, must include --aws-s3-report-name) Note: Use local directory path to populate a "local S3 bucket".
- *--aws-s3-report-name report_name*  (optional, must include --aws-s3-bucket-name)
- *--aws-s3-report-prefix prefix_name*  (optional)
- *--aws-finalize finalize_choice* (optional, choices: ['copy', 'overwrite'])
- *--ocp-cluster-id cluster-id* (required when providing ocp type)
- *--insights-upload UPLOAD_URL* (optional) Note: Use local directory path to populate a "local upload directory".
- *--static-report-file file_name* (optional) Note: Static report generation based on specified yaml file.  See example_aws[ocp]_static_data.yml for examples.
- *--gcp-report-prefix prefix_name*  (optional)
- *--gcp-bucket-name bucket_name*  (optional, see example usage below)

Note: If `--aws-s3-report-name` or `--aws-s3-report-prefix` are specified they should match what is configured in the AWS cost usage report settings.

Note: If `--aws-finalize` is used the *copy* choice will create a local copy of the data with a `-finalized` suffix and invoice id populated.
      If *overwrite* is used, the regular data file generated will have invoice id populated

Note: If `--insights-upload` is and pointing to a URL endpoint you must have INSIGHTS_USER and INSIGHTS_PASSWORD set in your environment.

Note: If `--static-report-file` is used start_date will default to first day of current month.  `start_date: last_month` will be first day of previous month.  `start_date: today` will start at the first hour of current day.  `end_date` can support relative days from the `start_date`. i.e `end_date: 2` is two days after start date.

Note: `--static-report-file` usage dates has a special `full_period` key value which will specify a usage for the entire `start_date - end_date` range.

AWS
---

Below is an example usage of ``nise`` for AWS data::

    nise --start-date 2018-06-03 --aws

    nise --start-date 2018-06-20 --aws --aws-s3-bucket-name testbucket --aws-s3-report-name cur

    nise --start-date 2018-06-20 --aws --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur

    nise --start-date 2018-06-20 --aws --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur --aws-s3-report-prefix my-prefix

    nise --start-date 2018-06-20 --aws --aws-finalize copy

    nise --aws --static-report-file aws_static_data.yml

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

OCP
---

Below is an example usage of ``nise`` for OCP data::

    nise --start-date 2018-06-03 --ocp --ocp-cluster-id test-001

    nise --start-date 2018-06-03 --ocp --ocp-cluster-id test-001 --insights-upload  https://cloud.redhat.com/api/ingress/v1/upload

    nise --start-date 2018-06-03 --ocp --ocp-cluster-id test-001 --insights-upload  /local/path/upload_dir

    nise --ocp --ocp-cluster-id my-cluster-id --static-report-file ocp_static_data.yml

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>.csv.

Below is an example usage of ``nise`` for OCP running on AWS data::

    # First ensure that the resource_id and dates in both AWS and OCP static report files match

    nise --aws --static-report-file examples/ocp_on_aws/aws_static_data.yml

    nise --ocp --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_aws/ocp_static_data.yml

Generated AWS reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

Generated OCP reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>.csv.

AZURE
-----

Note: To upload to AZURE, you must have AZURE_STORAGE_ACCOUNT and AZURE_ACCOUNT_KEY set in your environment.

Below is an example usage of ``nise`` for AZURE data::

    nise --start-date 2019-08-01 --azure

    nise --start-date 2019-08-01 --azure --azure-container-name container --azure-report-name cur

    nise --start-date 2019-08-01 --azure --azure-container-name /local/path/container --azure-report-name cur

    nise --start-date 2019-08-01 --azure --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix

    nise --start-date 2019-08-01 --azure --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix --static-report-file example_azure_static_data.yml

    nise --azure --static-report-file azure_static_data.yml

Below is an example usage of ``nise`` for OCP running on AZURE data::

    # First ensure that the dates in both AWS and OCP static report files match. Then specifcy an instance_id for Azure VMs in the Azure format where the string after the final '/' matches the OpenShift node_name.
        e.g. instance_id: '/subscriptions/99999999-9999-9999-9999-999999999999/resourceGroups/koku-99hqd-rg/providers/Microsoft.Compute/virtualMachines/master'
             node_name: master

    nise --azure --static-report-file examples/ocp_on_azure/azure_static_data.yml

    nise --ocp --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_azure/ocp_static_data.yml

Example upload to AZURE::

    AZURE_STORAGE_ACCOUNT=storage_account AZURE_ACCOUNT_KEY=key nise --start-date 2019-08-01 --azure --azure-container-name container --azure-report-prefix this_is_prefix  --azure-report-name this_is_report --static-report-file example_azure_static_data.yml

will put the generated reports in the :code:`container` container with the following structure::

    this_is_prefix/this_is_report/date_range/costreport_{uuid}.csv

To add an AZURE-local provider::

    {
        "name": "Test Azure Source",
        "type": "AZURE-local",
        "authentication": {
            "credentials": {
                "subscription_id": "12345678-1234-5678-1234-567812345678",
                "tenant_id": "12345678-1234-5678-1234-567812345678",
                "client_id": "12345678-1234-5678-1234-567812345678",
                "client_secret": "12345"
            }
        }, "billing_source": {
            "data_source": {
                "resource_group": {
                    "directory": --azure-report-prefix,
                    "export_name": --azure-report-name
                },
                "storage_account": {
                    "local_dir": "/tmp/local_container",
                    "container": ""
                }
            }
        }
    }


GCP
---

``--gcp-bucket-name`` could be an local file name or a bucket. When ``--gcp-bucket-name`` matches a file on disk,
the generated reports will be written to that file. If ``--gcp-bucket-name`` does not match a file on disk,
nise will attempt to upload the gnerated report to a bucket with that name. When this is the case
the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable must be set, and the given bucket-name must match
and existing bucket that is accessable by the service account indicated in ``GOOGLE_APPLICATION_CREDENTIALS``.

For more information about ``GOOGLE_APPLICATION_CREDENTIALS`` see `the Google Authentication Docs.
<https://cloud.google.com/docs/authentication/getting-started/>`_.


Below is an example usage of ``nise`` for GCP data::

    nise --gcp --start-date 2018-06-03 --end-date 2018-06-08

    nise --gcp --start-date 2018-06-03 --end-date 2018-06-08 --gcp-report-prefix my-gcp-data

    nise --gcp --start-date 2018-06-03 --end-date 2018-06-08 --gcp-report-prefix my-gcp-data --gcp-bucket-name my-gcp-bucket

    nise --gcp --static-report-file gcp_static_data.yml


Generated reports will be generated in daily .csv files with the file format <Report-Prefix>-<Year>-<Month>-<Day>.csv.


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
