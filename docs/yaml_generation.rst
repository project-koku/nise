Example ``nise yaml`` usage
=============================

AWS yamls
---------

To generate a yaml file which can be used to generate cost and usage reports we must supply 2 required arguments: ``-o output`` and ``-p provider``. The output is the output file location and the provider is the provider type (currently only AWS or OCP). The following command will output a yaml in the local directory using the default parameters of 1 of each AWS generator::

    nise yaml aws -o yaml_for_aws.yml

To use the built in large yaml generator config found in nise/yaml_generators/static, use this command::

    nise yaml aws -o large_aws.yml -c default

To use a user defined configuration, use this command::

    nise yaml aws -o aws.yml -c /path/to/config

The ``-r, --random`` flag can be added which will add a number of generators between 1 and the maximum defined in the configuration file. Start and end dates can be provided and they will overwrite the dates specified in the configuration. A user defined template may also be passed in using the ``-t /path/to/template`` flag. If a template is not passed in, the default found in ``nise/yaml_generators/static`` will be used.
