
Example ``nise report`` usage
=============================

nise is a command line tool::

    Usage:
        nise ( report | yaml )
        nise report ( aws | azure | gcp | ocp | oci ) [options]
        nise yaml ( aws | azure | ocp | ocp-on-cloud | oci ) [options]

    Report Options:
        -s, --start-date YYYY-MM-DD             required if not using --static-report-file FILE_NAME
                                                (static file dates overwrite this start date)
        -e, --end-date YYYY-MM-DD               optional, defaults:
                                                    AWS/GCP/OCP: today at 23:59
                                                    Azure: now() + 24 hours
        -w, --write-monthly                     optional, keep the generated report files in the local dir.
        --file-row-limit ROW_LIMIT              optional, default is 100,000. AWS and OCP only. Multiple reports
                                                will be generated with line counts not exceeding the ROW_LIMIT.
        --static-report-file YAML_NAME          optional, static report generation based on specified yaml file.
                                                See example_[provider]_static_data.yml for examples.

    AWS Report Options:
        --aws-s3-bucket-name BUCKET_NAME        optional, must include --aws-s3-report-name.
                                                Use local directory path to populate a "local S3 bucket".
        --aws-s3-report-name REPORT_NAME        optional, must include --aws-s3-bucket-name.
        --aws-s3-report-prefix PREFIX_NAME      optional
        --aws-finalize ( copy | overwrite )     optional, finalize choice

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
    OCI Report Options:
        --oci-bucket-name BUCKET_NAME           REQUIRED, if uploading to an OCI storage bucket

AWS reports
-----------

Generated reports will be generated in monthly .csv files with the file format <Month>-<Year>-<Report Name>.csv.

To generate completely random data and save the report files in the local directory, simply supply a ``--start-date YYYY-MM-DD`` and ``--write-monthly``::

    nise report aws --start-date 2020-05-03 --write-monthly

To generate a finalized report, the following will make a copy of the monthly report and append ``-finalized`` to the file name::

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

Below are example usages of ``nise`` for AZURE data::

    nise report azure --start-date 2019-08-01

    nise report azure --start-date 2019-08-01 --azure-container-name container --azure-report-name cur

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix

    nise report azure --start-date 2019-08-01 --azure-container-name /local/path/container --azure-report-name cur --azure-report-prefix my-prefix --static-report-file example_azure_static_data.yml

    nise report azure --static-report-file azure_static_data.yml

Example upload to AZURE::

    AZURE_STORAGE_ACCOUNT='my_storage_account' \
    AZURE_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=https;AccountName=my_storage_account;AccountKey=XXXXXXXXXXXXXXXXXXXXXXXXXX;EndpointSuffix=core.windows.net' \
    nise --start-date 2019-08-01 --azure --azure-container-name container --azure-report-prefix this_is_prefix  --azure-report-name this_is_report --static-report-file example_azure_static_data.yml

will put the generated reports in the :code:`container` container with the following structure::

    this_is_prefix/this_is_report/date_range/costreport_{uuid}.csv

GCP reports
-----------

``--gcp-bucket-name`` could be an local file name or a bucket. When ``--gcp-bucket-name`` matches a file on disk,
the generated reports will be written to that file. If ``--gcp-bucket-name`` does not match a file on disk,
nise will attempt to upload the generated report to a bucket with that name. When this is the case
the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable must be set, and the given bucket-name must match
and existing bucket that is accessable by the service account indicated in ``GOOGLE_APPLICATION_CREDENTIALS``.

For more information about ``GOOGLE_APPLICATION_CREDENTIALS`` see `the Google Authentication Docs.
<https://cloud.google.com/docs/authentication/getting-started/>`_.


Below are example usages of ``nise`` for GCP data::

    nise report gcp --start-date 2018-06-03 --end-date 2018-06-08

    nise report gcp --start-date 2018-06-03 --end-date 2018-06-08 --gcp-report-prefix my-gcp-data

    nise report gcp --start-date 2018-06-03 --end-date 2018-06-08 --gcp-report-prefix my-gcp-data --gcp-bucket-name my-gcp-bucket

    nise report gcp --static-report-file gcp_static_data.yml


Generated reports will be generated in daily .csv files with the file format <Report-Prefix>-<Year>-<Month>-<Day>.csv.


OCP reports
-----------

Generated reports will be produced in monthly .csv files with the file format <Month>-<Year>-<Cluster-ID>-<Report-type>.csv. Three report types are generated for each month: ``ocp_node_label``, ``ocp_pod_usage``, and ``ocp_storage_usage``.

Below are example usages of ``nise`` for OCP data::

To generate completely random data and save the report files in the local directory::

    nise report ocp -s 2020-06-03 -w --ocp-cluster-id test-001

To upload report files to ingress service::

    nise report ocp -s 2020-06-03 --ocp-cluster-id test-001 --insights-upload  <url to ingress>

To move the generated data into a specific local directory::

    nise report ocp  -s 2020-06-03 --ocp-cluster-id test-001 --insights-upload  /local/path/dir

To use a static yaml to generate data::

    nise report ocp --ocp-cluster-id my-cluster-id --static-report-file ocp_static_data.yml


OCP-on-Cloud reports
--------------------

Below is an example usage of ``nise`` for OCP running on AWS data using the `example ocp-on-aws yamls`_. This example will save the files to the local directory::

    # First ensure that the resource_id and dates in both AWS and OCP static report files match

    nise report aws -w --static-report-file examples/ocp_on_aws/aws_static_data.yml

    nise report ocp -w --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_aws/ocp_static_data.yml


Below is an example usage of ``nise`` for OCP running on AZURE data using the `example ocp-on-azure yamls`_. This example will save the files to the local directory::

    # First ensure that the dates in both AWS and OCP static report files match. Then specify an instance_id for Azure VMs in the Azure format where the string after the final '/' matches the OpenShift node_name.
        e.g. instance_id: '/subscriptions/99999999-9999-9999-9999-999999999999/resourceGroups/koku-99hqd-rg/providers/Microsoft.Compute/virtualMachines/master'
             node_name: master

    nise report azure -w --static-report-file examples/ocp_on_azure/azure_static_data.yml

    nise report ocp -w --ocp-cluster-id my-cluster-id --static-report-file examples/ocp_on_azure/ocp_static_data.yml


OCI reports
-----------

Generated reports will be produced in daily .csv files with the file format <reports>_<Report-type>-<csv>_<File-number>.csv.

The ``--oci-bucket-name`` options is used to attemp uploading the generated report to an OCI Storage bucket.
When this is the case, the ``OCI_CONFIG_FILE`` environment variable must be set, and the given bucket-name must match
an existing bucket that is accessable by the service account indicated in the ``OCI_CONFIG_FILE``.

Below are example usages of ``nise`` for OCI data::

To generate completely random data and save the report files in the local directory::

    nise report oci -s 2022-02-10 -w

To generate completely random data and upload the report files to an OCI Storage bucket::

    nise report oci -s 2022-02-10 --oci-bucket-name test-bucket

To generate less randomized data, supply a ``--static-report-file YAML_NAME``. `Example oci yaml.`_::

    nise report oci --static-report-file example_oci_static_data.yml




.. Links to repo files or directories

.. _`Example aws yaml.`: ../example_aws_static_data.yml

.. _`example ocp-on-aws yamls`: ../examples/ocp_on_aws

.. _`example ocp-on-azure yamls`: ../examples/ocp_on_azure

.. _`Example oci yaml.`: ../example_oci_static_data.yml
