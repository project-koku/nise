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

import yaml
from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator


def _load_yaml_file(filename):
    """Local data from yaml file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f'Cannot find file "{filename}"')
    yamlfile = None
    if filename:
        try:
            with open(filename, "r+") as yaml_file:
                yamlfile = yaml.safe_load(yaml_file)
        except TypeError:
            yamlfile = yaml.safe_load(filename)
    return yamlfile


def ocp_label_splitter(label):
    return [kv.split(":") for kv in [lab.split("_")[1] for lab in label.split("|")]]


def get_resourceid_and_tags(data):
    id_labels = {}
    for resource_id, tags in data.resourceid_labels.items():
        id_labels[resource_id] = [ocp_label_splitter(label) for label in tags]
    return id_labels


def get_validated_config(gen, args):
    config = gen.init_config(args)
    gen.validate_config(config)
    return config


def replace_args(args, yaml, provider, ocp_on_x, default=False):
    if not yaml:
        raise KeyError(f"{provider} is not defined under {ocp_on_x}")
    args.provider = provider
    args.output_file_name = yaml.get(f"{provider}-output-filename")
    if default:
        from nise.yaml_gen import STATIC_DIR

        args.template_file_name = os.path.join(STATIC_DIR, yaml.get(f"{provider}-template"))
        args.config_file_name = os.path.join(STATIC_DIR, yaml.get(f"{provider}-gen-config"))
    else:
        args.template_file_name = yaml.get(f"{provider}-template")
        args.config_file_name = yaml.get(f"{provider}-gen-config")


def run_generator(gen, args, config=None):
    if not config:
        config = gen.init_config(args)
    return gen.process_template(args, config)


class OCPonXGenerator:
    def __init__(self):
        self.aws = AWSGenerator
        self.azure = AzureGenerator
        self.ocp = OCPGenerator()

    def init_config(self, args):
        return

    def process_template(self, args, config):
        yaml_file = _load_yaml_file(args.config_file_name)
        if yaml_file.get("ocp-on-aws"):
            replace_args(args, yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws", yaml_file.get("default"))
            # First OCP:
            config = get_validated_config(self.ocp, args)
            data = run_generator(self.ocp, args, config)
            id_labels = get_resourceid_and_tags(data)

            # AWS:
            replace_args(args, yaml_file.get("ocp-on-aws").get("aws"), "aws", "ocp-on-aws", yaml_file.get("default"))
            self.aws = self.aws(id_labels)
            config = get_validated_config(self.aws, args)
            run_generator(self.aws, args, config)

        if yaml_file.get("ocp-on-azure"):
            replace_args(
                args, yaml_file.get("ocp-on-azure").get("ocp"), "ocp", "ocp-on-azure", yaml_file.get("default")
            )
            # Second OCP:
            config = get_validated_config(self.ocp, args)
            data = run_generator(self.ocp, args, config)
            id_labels = get_resourceid_and_tags(data)

            # Azure
            replace_args(
                args, yaml_file.get("ocp-on-azure").get("azure"), "azure", "ocp-on-azure", yaml_file.get("default")
            )
            self.azure = self.azure(id_labels)
            config = get_validated_config(self.azure, args)
            run_generator(self.azure, args, config)
