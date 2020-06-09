Example ``nise yaml`` usage
=============================

Yaml generation uses the following arguments::

    Usage:
        nise yaml ( aws | azure | ocp | ocp-on-cloud ) [options]

    Common YAML Options:
        -o, --output YAML_NAME                  REQUIRED, Output file path (i.e "large.yml").
        -c, --config ( CONFIG | default )       optional, Config file path. If "default" is provided,
                                                use internal config file
        -s, --start-date YYYY-MM-DD             optional, must include -e, --end-date
                                                    Start date (default is first day of last month)
        -e, --end-date YYYY-MM-DD               optional, must include -s, --start-date
                                                    End date (default is last day of current month)
        -r, --random                            optional, default=False
                                                    Randomize the number of
                                                        AWS: data generators
                                                        Azure: data generators
                                                        OCP: nodes, namespaces, pods, volumes, volume-claims
        -t, --template template                 optional, Template file path.

    OCP Yaml Options:
        -n, --num-nodes INT                     optional, Number of nodes to generate (used with OCP
                                                only; default is 1)

    OCP-on-Cloud Options:
        -c, --config ( CONFIG | default )       REQUIRED, Config file path. If "default" is provided,
                                                use internal config file
        -n, --num-nodes INT                     optional, Number of nodes to generate (default is 1)


For AWS, Azure, and OCP, an output file name must be supplied. This file name will be the name of the generated yaml file. For the ``-c, --config`` option, either the value ``default`` can be supplied or the path to a configuration file may be given. If using the ``default`` keyword, the `internal configuration found in nise/yaml_generators/static`_ will be used.

AWS yamls
---------

To generate a yaml file which can be used to generate cost and usage reports we must supply 2 required arguments: ``-o output`` and ``-p provider``. The output is the output file location and the provider is the provider type (currently only AWS or OCP). The following command will output a yaml in the local directory using the default parameters of 1 of each AWS generator::

    nise yaml aws -o yaml_for_aws.yml

To use the built in large yaml generator config found in nise/yaml_generators/static, use this command::

    nise yaml aws -o large_aws.yml -c default

To use a user defined configuration, use this command::

    nise yaml aws -o aws.yml -c /path/to/config

The ``-r, --random`` flag can be added which will add a number of generators between 1 and the maximum defined in the configuration file. Start and end dates can be provided and they will overwrite the dates specified in the configuration. A user defined template may also be passed in using the ``-t /path/to/template`` flag. If a template is not passed in, the default found in ``nise/yaml_generators/static`` will be used.


.. _`internal configuration found in nise/yaml_generators/static`: ../nise/yaml_generators/static
