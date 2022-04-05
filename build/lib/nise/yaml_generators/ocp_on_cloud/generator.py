#
# Copyright 2020 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import os

from nise.util import LOG
from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator


def ocp_label_splitter(label):
    """Split the OCP lables into key, value pairs."""
    return [kv.split(":") for kv in [lab.split("_")[1] for lab in label.split("|")]]


def get_resourceid_and_tags(data):
    """Convert the OCP resource ids and lables into usable list."""
    id_labels = {}
    for resource_id, tags in data.resourceid_labels.items():
        id_labels[resource_id] = [ocp_label_splitter(label) for label in tags]
    return id_labels


def get_validated_config(gen, args):
    """Get the validated configuration for the specified generator."""
    config = gen.init_config(args)
    gen.validate_config(config)
    return config


def replace_args(args, yaml, provider, ocp_on_cloud):
    """Replace appropriate file paths in args."""
    if not yaml:
        raise KeyError(f"Options YAML error: {provider} is not defined under {ocp_on_cloud}")
    from nise.yaml_gen import STATIC_DIR

    args.provider = provider

    if yaml.get(f"{provider}-output-filename"):
        args.output_file_name = yaml.get(f"{provider}-output-filename")
    else:
        LOG.info(
            f"Output file not defined for {provider} under {ocp_on_cloud}. Writing to '{ocp_on_cloud}_{provider}.yml'."
        )
        args.output_file_name = f"{ocp_on_cloud}_{provider}.yml"

    if args.default:
        template_file_name = os.path.join(STATIC_DIR, yaml.get(f"{provider}-template"))
        config_file_name = os.path.join(STATIC_DIR, yaml.get(f"{provider}-gen-config"))
    else:
        template_file_name = yaml.get(f"{provider}-template")
        config_file_name = yaml.get(f"{provider}-gen-config")

    if template_file_name:
        args.template_file_name = template_file_name
    else:
        LOG.info(f"Template not defined for {provider} under {ocp_on_cloud}. Using default template.")
        args.template_file_name = os.path.join(STATIC_DIR, f"{provider}_static_data.yml.j2")
    if config_file_name:
        args.config_file_name = config_file_name
    else:
        LOG.info(f"Configuration not defined for {provider} under {ocp_on_cloud}. Using default configuration.")
        args.config_file_name = None


def run_generator(gen, args, config=None):
    """Generate the yaml files for the specified generator."""
    if not config:
        config = gen.init_config(args)
    return gen.process_template(args, config)


class OCPonCloudGenerator:
    """Class used to create unique OCP-on-Cloud yaml files."""

    def __init__(self):
        self.aws = AWSGenerator
        self.azure = AzureGenerator
        self.ocp = OCPGenerator()

    def init_config(self, args):
        """Skip init-config for ocp-on-cloud.

        Init config is called for each provider using its dedicated generator.

        """
        return

    def process_template(self, args, config=None):
        """Process specific provider configs to produce yamls."""
        from nise.util import load_yaml

        yaml_file = load_yaml(args.config_file_name)
        if yaml_file.get("ocp-on-aws"):
            replace_args(args, yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
            # First OCP:
            config = get_validated_config(self.ocp, args)
            data = run_generator(self.ocp, args, config)
            id_labels = get_resourceid_and_tags(data)

            # AWS:
            replace_args(args, yaml_file.get("ocp-on-aws").get("aws"), "aws", "ocp-on-aws")
            self.aws = self.aws(id_labels)
            config = get_validated_config(self.aws, args)
            run_generator(self.aws, args, config)

        if yaml_file.get("ocp-on-azure"):
            replace_args(args, yaml_file.get("ocp-on-azure").get("ocp"), "ocp", "ocp-on-azure")
            # Second OCP:
            config = get_validated_config(self.ocp, args)
            data = run_generator(self.ocp, args, config)
            id_labels = get_resourceid_and_tags(data)

            # Azure
            replace_args(args, yaml_file.get("ocp-on-azure").get("azure"), "azure", "ocp-on-azure")
            self.azure = self.azure(id_labels)
            config = get_validated_config(self.azure, args)
            run_generator(self.azure, args, config)
