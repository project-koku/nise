===========
Working with Masu
===========
~~~~~
About
~~~~~

Nise is a developer tool for generating sample cost and use data for testing purposes. Although nise can generate standalone reports, its most common use case is to create reports to be consumed by `koku's <https://github.com/project-koku/koku>`_ python module masu. This section provides a walkthrough for how to use nise along with masu to generate providers in koku.

OCP Providers
=============
In order to create any ocp providers with masu, nise will need to place the csv files in the masu expected location. Masu expects the files to be placed under koku's :code:`testing/pvc_dir/insights_local` `directory <https://github.com/project-koku/koku/tree/master/testing/pvc_dir>`_. If :code:`insights_local` does not exist yet you will have to create it.

Basic OCP provider
------------------
**Step One: The Nise Command**

To create a basic OCP provider you will have to provide three key peices of information.

   1. :code:`--ocp-cluster-id $(cluster_id)` <string> Ex. my-cluster_id
   2. :code:`--insights-upload testing/pvc_dir/insights_local` Masu Expected location
   3. :code:`--static-report-file $(srf_yaml)` Path to a static report `file <https://github.com/project-koku/nise/blob/master/example_aws_static_data.yml>`_

.. highlight:: bash

::

  nise --ocp --ocp-cluster-id $(cluster_id) --insights-upload testing/pvc_dir/insights_local --static-report-file $(srf_yaml)
.. highlight:: none

**Step Two: Create the Provider**

After creating the csvs under the :code:`insights_local` directory, the provider will then need to be added by posting to the provider endpoint.

.. highlight:: bash

::

   curl -d '{"name": "OCP_PROVIDER_NAME", "type": "OCP", "authentication": {"provider_resource_name": "$(cluster_id)"}}' -H "Content-Type: application/json" -X POST http://0.0.0.0:8000/api/cost-management/v1/providers/

.. highlight:: none

- The :code:`$(cluster_id)` must match the cluster_id provided in the nise command.

**Step Three: Trigger Masu**

You can trigger Masu by hitting the download endpoint: http://127.0.0.1:5000/api/cost-management/v1/download/

OCP on AWS Provider
-------------------
In order to create an OCP on AWS provider, you must first create an ocp provider and then an aws provider. Each provider will need to be created from a static report file, and the resource_id and dates in both AWS and OCP static report files match.

**Step One: Create the OCP provider**

The steps to create the ocp provider will be the exact same as the `Basic OCP provider`_ steps above, except you must use the static file under the :code:`ocp_on_aws` example `here <https://github.com/project-koku/nise/blob/master/examples/ocp_on_aws/ocp_static_data.yml>`_.

**Step Two: The AWS nise command**

To create a basic AWS provider you will have to provide three key peices of information.

   1. :code:`--aws-s3-report-name $(report_name)` <string> Ex. testing_magic
   2. :code:`--aws-s3-bucket-name testing/local_providers/aws_local` Masu Expected location
   3. :code:`--static-report-file $(srf_yaml)` Path to a static report file

- The static report file must be matching pair to the ocp file where the resource_id & dates are the same. The file must be the matching `file <https://github.com/project-koku/nise/blob/master/examples/ocp_on_aws/aws_static_data.yml>`_ in the example.

.. highlight:: bash

::

  nise --aws --static-report-file $(srf_yaml) --aws-s3-bucket-name testing/local_providers/aws_local --aws-s3-report-name $(report_name)
.. highlight:: none

**Step Three: Create the AWS provider**

After running the nise command and creating the csv files, you will need to create the aws command with the following curl command.

.. highlight:: bash

::

  curl -d '{"name": "$(report_name)", "type": "AWS-local", "authentication": {"provider_resource_name": "$(report_name)"},"billing_source": {"bucket": "/tmp/local_bucket"}}' -H "Content-Type: application/json" -X POST http://0.0.0.0:8000/api/cost-management/v1/providers/
.. highlight:: none

- The bucket value for the curl command can be a little confusing. You are not providing the same bucket name as the nise command, but instead the container directory in the volume mapping which can be found `here <https://github.com/project-koku/koku/blob/master/docker-compose.yml#L174>`_. For example, since we used :code:`aws_local` in our nise command the curl command will use :code:`/tmp/local_bucket`
- The provider type in the curl command must be :code:`AWS-local` in order to avoid ARN syntax checking.

**Step Four: Trigger Masu**

You can trigger Masu by hitting the download endpoint: http://127.0.0.1:5000/api/cost-management/v1/download/
