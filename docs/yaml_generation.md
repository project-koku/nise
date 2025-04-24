YAML generation uses the following arguments:

    Usage:
        nise yaml ( aws | azure | ocp | ocp-on-cloud ) [options]

    Common yaml Options:
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

    OCP YAML Options:
        -n, --num-nodes INT                     optional, Number of nodes to generate (used with OCP
                                                only; default is 1)

    OCP-on-Cloud Options:
        -c, --config ( CONFIG | default )       REQUIRED, Config file path. If "default" is provided,
                                                use internal config file
        -n, --num-nodes INT                     optional, Number of nodes to generate (default is 1)

For AWS, Azure and OCP an output file name must be supplied. This file name will be the name of the generated YAML file. For the `-c, --config` option, either the value `default` can be supplied or the path to a configuration file may be given. If using the `default` keyword, the [internal configuration](../nise/yaml_generators/static) will be used. If the configuration argument is omitted, Nise will generate the smallest YAML possible based on the given template (this means 1 node, 1 generator, etc.). Start and end dates can be supplied on the command line or in the configuration file. The configuration file dates take precedence over the CLI arguments. If using the `-r, --random` argument, the number of nodes, generators, and labels will vary between 1 (or 0) and the maximum values defined by the configuration. The `-t, --template` argument can be omitted to use the default template.

For OCP-on-Cloud YAML generation, things are more complicated. OCP is linked to AWS through resource-id or tags, whereas OCP is linked to Azure through instance-id/node-name or tags. To ensure there are no overlapping namespaces or tags, all of the YAMLs should be generated simluatenously which means all of the configurations for AWS, Azure, OCP for AWS, and OCP for Azure need to be specified, including the generator configurations, the templates, and the output files. To accomplish this, a unique configuration file containing all of the configuration information is supplied. Just like with the individual providers, [a built-in configuration is included]() To make use of the built-in configuration, supply `default` to the `-c, --config` argument.

# Examples

## AWS YAMLs

To generate a YAML file which can be used to generate cost and usage reports we must supply 1 required argument: `-o, --output YAML_NAME`. The output is the output file location. The following command will output a YAML in the local directory using the default parameters of 1 of each AWS generator:

    nise yaml aws -o YAML_for_aws.yml

To use the built in large YAML generator config [found here](../nise/yaml_generators/static/aws_generator_config.yml), use this command:

    nise yaml aws -o large_aws.yml -c default

To use a user defined configuration, use this command:

    nise yaml aws -o aws.yml -c /path/to/config

The `-r, --random` flag can be added which will add a number of generators between 0 and the maximum defined in the configuration file. A user defined template may also be passed in using the `-t /path/to/template` flag. If a template is not passed in, the [default will be used](../nise/yaml_generators/static/aws_static_data.yml.j2).

## Azure YAMLs

The examples listed above for AWS also apply for Azure. Simply switch out `aws` for `azure`.

## OCP YAMLs

In addition to the examples above, OCP takes an additional optional argument: `-n, --num-nodes`. This value specifies the maximum number of nodes to generate and over-writes the max value given in the configuration file.

## OCP-on-Cloud YAMLs

The most straightforward way to generate the necessary YAMLs for ocp-on-cloud reports is to use the default configuration:

    nise yaml ocp-on-cloud -c default

The above command uses the [ocp_on_cloud_options.yml](../nise/yaml_generators/static/ocp_on_cloud_options.yml) file. To generate only OCP-on-AWS or OCP-on-Azure, a custom configuration must be supplied which only contains the necessary configuration (e.g. for OCP-on-AWS, the file should only contain the ocp-on-aws fields and exclude all the ocp-on-azure fields.)


[a built-in configuration is included]: ../nise/yaml_generators/static/ocp_on_cloud_options.yml
