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
import argparse
import os
import shutil
from datetime import datetime
from importlib import import_module
from unittest import TestCase

from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator
from nise.yaml_generators.ocp_on_cloud import generator
from nise.yaml_generators.ocp_on_cloud.generator import get_resourceid_and_tags
from nise.yaml_generators.ocp_on_cloud.generator import get_validated_config
from nise.yaml_generators.ocp_on_cloud.generator import replace_args
from nise.yaml_generators.ocp_on_cloud.generator import run_generator


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
GEN_FILE_DIR = os.path.dirname(os.path.abspath(generator.__file__))
CACHE_PATH = os.path.join(os.path.dirname(GEN_FILE_DIR), "__pycache__")


class OCPGeneratorTestCase(TestCase):
    """
    Base TestCase class, for OCP yaml gen.
    """

    @classmethod
    def setUpClass(cls):
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)

        cls.module = import_module("nise.yaml_generators.ocp_on_cloud.generator")
        cls.yg = cls.module.OCPonCloudGenerator()

    def setUp(self):
        args = argparse.Namespace()
        args.default = True
        args.provider = "ocp-on-cloud"
        args.config_file_name = None
        args.template_file_name = None
        args.start_date = datetime.today().replace(day=1).date()
        args.end_date = datetime.today().date()
        args.num_nodes = None
        args.random = False
        self.args = args
        self.ocp = OCPGenerator()
        self.aws = AWSGenerator
        self.azure = AzureGenerator

    def test_cache(self):
        """Test that labels and resource_ids are unique between ocp-on-aws and ocp-on-azure."""
        yaml_file = {
            "ocp-on-aws": {
                "ocp": {
                    "ocp-template": "ocp_static_data.yml.j2",
                    "ocp-gen-config": "ocp_generator_config.yml",
                    "ocp-output-filename": "ocp-on-aws_ocp.yml",
                },
                "aws": {
                    "aws-template": "aws_static_data.yml.j2",
                    "aws-gen-config": "aws_generator_config.yml",
                    "aws-output-filename": "ocp-on-aws_aws.yml",
                },
            },
            "ocp-on-azure": {
                "ocp": {
                    "ocp-template": "ocp_static_data.yml.j2",
                    "ocp-gen-config": "ocp_generator_config.yml",
                    "ocp-output-filename": "ocp-on-azure_ocp.yml",
                },
                "azure": {
                    "azure-template": "azure_static_data.yml.j2",
                    "azure-gen-config": "azure_generator_config.yml",
                    "azure-output-filename": "ocp-on-azure_azure.yml",
                },
            },
        }

        try:
            replace_args(self.args, yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
            self.args.config_file_name = None
            config = get_validated_config(self.ocp, self.args)
            config.max_nodes = 1000
            data = run_generator(self.ocp, self.args, config)
            id_labels_1 = get_resourceid_and_tags(data)
        finally:
            os.remove(yaml_file["ocp-on-aws"]["ocp"]["ocp-output-filename"])

        try:
            replace_args(self.args, yaml_file.get("ocp-on-azure").get("ocp"), "ocp", "ocp-on-azure")
            self.args.config_file_name = None
            config = get_validated_config(self.ocp, self.args)
            config.max_nodes = 1000
            data = run_generator(self.ocp, self.args, config)
            id_labels_2 = get_resourceid_and_tags(data)
        finally:
            os.remove(yaml_file["ocp-on-azure"]["ocp"]["ocp-output-filename"])

        for key in id_labels_1.keys():
            self.assertNotIn(key, id_labels_2.keys())

        for namespace_values in id_labels_1.values():
            for values in namespace_values:
                for value in values:
                    for namespace_values2 in id_labels_2.values():
                        for values2 in namespace_values2:
                            self.assertNotIn(value, values2)
