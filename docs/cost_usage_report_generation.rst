
Example ``nise report`` usage
=============================

AWS reports
-----------

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

To generate completely random data and save the report files in the local directory, simply supply a ``--start-date YYYY-MM-DD`` and ``--write-monthly``::

    nise report aws --start-date 2020-05-03 --write-monthly

To generate a finalized report, the following will make a copy of the monthly report and append ``-finalized`` to the file name.

    nise report aws -s 2020-05-03 --aws-finalize copy

To upload data to an AWS bucket::

    nise report aws -s 2020-05-03 --aws-s3-bucket-name testbucket --aws-s3-report-name cur

To move the generated data into a specific local directory, supply ``--aws-s3-bucket-name`` with a ``/path/to/local/dir``::

    nise report aws -s 2020-05-03 --aws-s3-bucket-name /local/path/testbucket --aws-s3-report-name cur

To generate less randomized data, supply a ``--static-report-file YAML_NAME``. `Example aws yaml.`_::

    nise report aws --static-report-file example_aws_static_data.yml


AZURE reports
-------------

Note: To upload to AZURE, you must have AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_CONNECTION_STRING set in your environment.

Below is an example usage of ``nise`` for AZURE data::

    nise report azure --start-date 2019-08-01

    nise report azure --start-date 2019-08-01 --azure-container-name container --azure-report-name cur

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix --static-report-file example_azure_static_data.yml

    nise report azure --static-report-file azure_static_data.yml



OCP reports
-----------

Generated reports will be poduced in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>-<Report-type>.csv. Three report types are generated for each month: ``ocp_node_label``, ``ocp_pod_usage``, and ``ocp_storage_usage``.

Below is an example usage of ``nise`` for OCP data::

To generate completely random data and save the report files in the local directory::

    nise report ocp -s 2020-06-03 -w --ocp-cluster-id test-001

To upload report files to ingress service::

    nise report ocp -s 2020-06-03 --ocp-cluster-id test-001 --insights-upload  <url to ingress>

To move the generated data into a specific local directory::

    nise reprot ocp  -s 2020-06-03 --ocp-cluster-id test-001 --insights-upload  /local/path/dir

To use a static yaml to generate data::

    nise report ocp --ocp-cluster-id my-cluster-id --static-report-file ocp_static_data.yml






Below is an example usage of ``nise`` for OCP running on AZURE data::

    # First ensure that the dates in both AWS and OCP static report files match. Then specify an instance_id for Azure VMs in the Azure format where the string after the final '/' matches the OpenShift node_name.
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




Generating OCP-on-AWS (or Azure) can use any of the

Below is an example usage of ``nise`` for OCP running on AWS data. `Example ocp-on-aws yamls`_::

    # First ensure that the resource_id and dates in both AWS and OCP static report files match

    nise report aws -w --static-report-file examples/ocp_on_aws/aws_static_data.yml

    nise report ocp -w --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_aws/ocp_static_data.yml





.. _`Example aws yaml.`: example_aws_static_data.yml

.. _`Example ocp-on-aws yamls`: examples/ocp_on_aws
