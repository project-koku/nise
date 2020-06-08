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

Testing
-------

Nise uses tox to standardize the environment used when running tests. Essentially, tox manages its own virtual environment and a copy of required dependencies to run tests. To ensure a clean tox environment run ::

    tox -r

This will rebuild the tox virtual env and then run all tests.

To run unit tests specifically::

    tox -e py36

Linting
-------
This repository uses `pre-commit`_ to check and enforce code style. It uses `Black`_ to reformat the Python code and `Flake8`_ to check it
afterwards. Other formats and text files are linted as well.

To run pre-commit checks::

    pre-commit run --all-files


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


Note: If ``--aws-s3-report-name`` or ``--aws-s3-report-prefix`` are specified they should match what is configured in the AWS cost usage report settings.

Note: If ``--aws-finalize`` is used the *copy* choice will create a local copy of the data with a ``-finalized`` suffix and invoice id populated.
      If *overwrite* is used, the regular data file generated will have invoice id populated

Note: If ``--insights-upload`` is and pointing to a URL endpoint you must have INSIGHTS_USER and INSIGHTS_PASSWORD set in your environment.
      Payloads for insights uploads will be split on a per-file basis.

Note: If ``--static-report-file`` is used start_date will default to first day of current month.  ``start_date: last_month`` will be first day of previous month.  ``start_date: today`` will start at the first hour of current day.  ``end_date`` can support relative days from the ``start_date``. i.e ``end_date: 2`` is two days after start date.

Note: ``--static-report-file`` usage dates has a special ``full_period`` key value which will specify a usage for the entire ``start_date - end_date`` range.


------------
Contributing
------------

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
