===========
Nise README
===========
|license| |PyPI| |Build Status| |Unittests| |codecov| |Updates|

-----
About
-----

A tool for generating sample cost and usage data for testing purposes.

---------------
Getting Started
---------------

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

For generating sample data for developing or testing Koku, please refer to `Ingesting Nise data with Koku <https://github.com/project-koku/nise/blob/master/docs/working_with_masu.rst>`_.

Testing and Linting
-------------------

Nise uses tox to standardize the environment used when running tests. Essentially, tox manages its own virtual environment and a copy of required dependencies to run tests. To ensure a clean tox environment run ::

    tox -r

This will rebuild the tox virtual env and then run all tests.

To run unit tests specifically::

    tox -e py36

To lint the code base ::

    tox -e lint

Nise and IQE Tests
------------------

The iqe tests use nise to generate mock data; therefore, we need to ensure that our nise changes do not break the iqe tests. To do this you will need to copy the `.env.example` to a `.env` file.
After the `.env` file is configured you will then need to run ::

    make run-iqe

The `make run-iqe` command by default will run the smoke tests. However, if you want to run a specific iqe test command you can pass it in through the `IQE_CMD` parameter ::

    make run-iqe IQE_CMD='iqe tests plugin hccm -k test_api_aws_provider_create_foo_resource_name'


Publishing
----------

Please remember to sync your updated dependecies to setup.py with ::

    pipenv-setup sync -p

After that, make sure to increment the version in setup.py. As soon as your PR is merged to master, a new koku-nise package will built, tagged, and deployed to PyPI.

Finer Publishing Details
________________________

All of the deployment is driven entirely by a Github Action workflow, so if issues ever crop up, start in ``publish-to-pypi.yml``. When a branch is merged into master, the Action will kick off. There are three things that must happen before a deployment is successful, a successful artifact build, dependencies verified in sync between the requirements files, and setup.py, and the tag must not yet exist in git. The dependency syncing/verification is done with the `pipenv-setup <https://github.com/Madoshakalaka/pipenv-setup>`_ tool. After the artifact is deployed, it'll be available at `PyPI <https://pypi.org/project/koku-nise/#history>`_.

Prereqs
=======

- AWS population requires prior setup of AWS Cost and Usage Report of same name to be created, as well as associated Bucket, Policy, Role, etc.

-----
Usage
-----
nise is a command line tool::

    Usage:
        nise ( report | yaml )
        nise report ( aws | azure | gcp | ocp ) [options]
        nise yaml ( aws | azure | ocp ) [options]

    Report Options:
        --start-date YYYY-MM-DD             optional, not supplied if using --static-report-file FILE_NAME
        --end-date YYYY-MM-DD               optional, defaults to today and current hour
        --file-row-limit ROW_LIMIT          optional, default is 100,000. AWS and OCP only. Multiple reports
                                            will be generated with line counts not exceeding the ROW_LIMIT.
        --static-report-file YAML_NAME      optional, static report generation based on specified yaml file.
                                            See example_[provider]_static_data.yml for examples.
        --write-monthly                     optional, keep the generated report files.

    AWS Report Options:
        --aws-s3-bucket-name BUCKET_NAME            optional, must include --aws-s3-report-name.
                                                    Use local directory path to populate a "local S3 bucket".
        --aws-s3-report-name REPORT_NAME            optional, must include --aws-s3-bucket-name.
        --aws-s3-report-prefix PREFIX_NAME          optional
        --aws-finalize ( copy | overwrite )         optional, finalize choice

    Azure Report Options:
        --azure-container-name
        --azure-report-name
        --azure-report-prefix

    GCP Report Options:
        --gcp-report-prefix PREFIX_NAME
        --gcp-bucket-name BUCKET_NAME

    OCP Report Options:
        --ocp-cluster-id CLUSTER_ID             REQUIRED
        --insights-upload UPLOAD_URL            optional, Use local directory path to populate a
                                                "local upload directory".

    YAML Options:
        -o, --output YAML_NAME                  REQUIRED, Output file path (i.e "large.yml").
        -c, --config ( CONFIG | default )       optional, Config file path. If "default" is provided,
                                                use internal config file
        -s, --start-date YYYY-MM-DD             optional, must include --end-date
                                                    Start date (overrides template, default is first
                                                    day of last month)
        -e, --end-date YYYY-MM-DD               optional, must include --start-date
                                                    End date (overrides template, default is last day
                                                    of current month)
        -n, --num-nodes INT                     optional, Number of nodes to generate (used with OCP
                                                only; overrides template, default is 1)
        -r, --random                            optional, default=False
                                                    Randomize the number of
                                                        AWS: data generators
                                                        Azure: data generators
                                                        OCP: nodes, namespaces, pods, volumes, volume-claims
        -t, --template template                 optional, Template file path.


Note: If `--aws-s3-report-name` or `--aws-s3-report-prefix` are specified they should match what is configured in the AWS cost usage report settings.

Note: If `--aws-finalize` is used the *copy* choice will create a local copy of the data with a `-finalized` suffix and invoice id populated.
      If *overwrite* is used, the regular data file generated will have invoice id populated

Note: If `--insights-upload` is and pointing to a URL endpoint you must have INSIGHTS_USER and INSIGHTS_PASSWORD set in your environment.
      Payloads for insights uploads will be split on a per-file basis.

Note: If `--static-report-file` is used start_date will default to first day of current month.  `start_date: last_month` will be first day of previous month.  `start_date: today` will start at the first hour of current day.  `end_date` can support relative days from the `start_date`. i.e `end_date: 2` is two days after start date.

Note: `--static-report-file` usage dates has a special `full_period` key value which will specify a usage for the entire `start_date - end_date` range.


``nise`` examples
=================

AWS reports
-----------

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

To generate completely random data and save the report files in the local directory, simply supply a ``--start-date YYYY-MM-DD`` and ``--write-monthly``::

    nise report aws --start-date 2020-05-03 --write-monthly

To upload data to an AWS bucket::

    nise report aws start-date 2020-05-03 --aws-s3-bucket-name testbucket --aws-s3-report-name cur

To move put the generated data into a specific local directory, supply ``--aws-s3-bucket-name`` with a ``/path/to/local/dir``::

    nise report aws --start-date 2020-05-03 --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur

    nise report aws --start-date 2020-05-03 --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur --aws-s3-report-prefix my-prefix

    nise report aws --start-date 2018-06-20 --aws-finalize copy

To generate static data, supply a ``--static-report-file YAML_NAME``. And example yaml is found in ``example_aws_static_data.yml``::

    nise report aws --static-report-file example_aws_static_data.yml

AWS yamls
---------

To generate a yaml file which can be used to generate cost and usage reports we must supply 2 required arguments: ``-o output`` and ``-p provider``. The output is the output file location and the provider is the provider type (currently only AWS or OCP). The following command will output a yaml in the local directory using the default parameters of 1 of each AWS generator::

    nise yaml aws -o yaml_for_aws.yml

To use the built in large yaml generator config found in nise/yaml_generators/static, use this command::

    nise yaml aws -o large_aws.yml -c default

To use a user defined configuration, use this command::

    nise yaml aws -o aws.yml -c /path/to/config

The ``-r, --random`` flag can be added which will add a number of generators between 1 and the maximum defined in the configuration file. Start and end dates can be provided and they will overwrite the dates specified in the configuration. A user defined template may also be passed in using the ``-t /path/to/template`` flag. If a template is not passed in, the default found in ``nise/yaml_generators/static`` will be used.

OCP
---

Below is an example usage of ``nise`` for OCP data::

    nise report ocp --start-date 2018-06-03 --ocp-cluster-id test-001

    nise report ocp --start-date 2018-06-03 --ocp-cluster-id test-001 --insights-upload  https://cloud.redhat.com/api/ingress/v1/upload

    nise reprot ocp --start-date 2018-06-03 --write-monthly --ocp-cluster-id test-001 --insights-upload  /local/path/upload_dir

    nise report ocp --ocp-cluster-id my-cluster-id --static-report-file ocp_static_data.yml

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>.csv.

Below is an example usage of ``nise`` for OCP running on AWS data::

    # First ensure that the resource_id and dates in both AWS and OCP static report files match

    nise report aws --static-report-file examples/ocp_on_aws/aws_static_data.yml

    nise report ocp --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_aws/ocp_static_data.yml

Generated AWS reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

Generated OCP reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>.csv.

AZURE
-----

Note: To upload to AZURE, you must have AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_CONNECTION_STRING set in your environment.

Below is an example usage of ``nise`` for AZURE data::

    nise report azure --start-date 2019-08-01

    nise report azure --start-date 2019-08-01 --azure-container-name container --azure-report-name cur

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix --static-report-file example_azure_static_data.yml

    nise report azure --static-report-file azure_static_data.yml

Below is an example usage of ``nise`` for OCP running on AZURE data::

    # First ensure that the dates in both AWS and OCP static report files match. Then specifcy an instance_id for Azure VMs in the Azure format where the string after the final '/' matches the OpenShift node_name.
        e.g. instance_id: '/subscriptions/99999999-9999-9999-9999-999999999999/resourceGroups/koku-99hqd-rg/providers/Microsoft.Compute/virtualMachines/master'
             node_name: master

    nise report azure --static-report-file examples/ocp_on_azure/azure_static_data.yml

    nise report ocp --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_azure/ocp_static_data.yml

Example upload to AZURE::

    AZURE_STORAGE_ACCOUNT='my_storage_account' \
    AZURE_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=https;AccountName=my_storage_account;AccountKey=XXXXXXXXXXXXXXXXXXXXXXXXXX;EndpointSuffix=core.windows.net' \
    nise --start-date 2019-08-01 --azure --azure-container-name container --azure-report-prefix this_is_prefix  --azure-report-name this_is_report --static-report-file example_azure_static_data.yml

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

    nise report gcp --start-date 2018-06-03 --end-date 2018-06-08

    nise report gcp --start-date 2018-06-03 --end-date 2018-06-08 --gcp-report-prefix my-gcp-data

    nise report gcp --start-date 2018-06-03 --end-date 2018-06-08 --gcp-report-prefix my-gcp-data --gcp-bucket-name my-gcp-bucket

    nise report gcp --static-report-file gcp_static_data.yml


Generated reports will be generated in daily .csv files with the file format <Report-Prefix>-<Year>-<Month>-<Day>.csv.

Linting
-------
This repository uses `pre-commit`_ to check and enforce code style. It uses `Black`_ to reformat the Python code and `Flake8`_ to check it
afterwards. Other formats and text files are linted as well.

To run pre-commit checks::

    pre-commit run --all-files

Contributing
=============

Please refer to Contributing_.

.. _Contributing: https://github.com/project-koku/nise/blob/master/CONTRIBUTING.rst
.. _pre-commit: https://pre-commit.com
.. _Black: https://github.com/psf/black
.. _Flake8: http://flake8.pycqa.org

.. |license| image:: https://img.shields.io/github/license/project-koku/nise.svg
   :target: https://github.com/project-koku/nise/blob/master/LICENSE
.. |Build Status| image:: https://github.com/project-koku/nise/workflows/Publish/badge.svg?branch=master
   :target: https://github.com/project-koku/nise/actions
.. |Unittests| image:: https://github.com/project-koku/nise/workflows/Unit%20Tests/badge.svg
   :target: https://github.com/project-koku/nise/actions
.. |codecov| image:: https://codecov.io/gh/project-koku/nise/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/project-koku/nise
.. |Updates| image:: https://pyup.io/repos/github/project-koku/nise/shield.svg?t=1524249231720
   :target: https://pyup.io/repos/github/project-koku/nise/
.. |PyPI| image:: https://badge.fury.io/py/koku-nise.svg
   :target: https://badge.fury.io/py/koku-nise
