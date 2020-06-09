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
from unittest.mock import patch

from faker import Faker
from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator
from nise.yaml_generators.ocp_on_cloud import generator
from nise.yaml_generators.ocp_on_cloud.generator import get_resourceid_and_tags
from nise.yaml_generators.ocp_on_cloud.generator import get_validated_config
from nise.yaml_generators.ocp_on_cloud.generator import replace_args
from nise.yaml_generators.ocp_on_cloud.generator import run_generator


FAKE = Faker()
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
GEN_FILE_DIR = os.path.dirname(os.path.abspath(generator.__file__))
CACHE_PATH = os.path.join(os.path.dirname(GEN_FILE_DIR), "__pycache__")


def mock_replace_args(args, yaml, provider, ocp_on_cloud):
    """Replace the config_file_name with none to use the default config."""
    replace_args(args, yaml, provider, ocp_on_cloud)
    args.config_file_name = None
    return args


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

        self.yaml_file = {
            "ocp-on-aws": {
                "ocp": {
                    "ocp-template": "ocp_static_data.yml.j2",
                    "ocp-gen-config": "ocp_generator_config.yml",
                    "ocp-output-filename": f"tmp_{FAKE.ean8()}.yml",
                },
                "aws": {
                    "aws-template": "aws_static_data.yml.j2",
                    "aws-gen-config": "aws_generator_config.yml",
                    "aws-output-filename": f"tmp_{FAKE.ean8()}.yml",
                },
            },
            "ocp-on-azure": {
                "ocp": {
                    "ocp-template": "ocp_static_data.yml.j2",
                    "ocp-gen-config": "ocp_generator_config.yml",
                    "ocp-output-filename": f"tmp_{FAKE.ean8()}.yml",
                },
                "azure": {
                    "azure-template": "azure_static_data.yml.j2",
                    "azure-gen-config": "azure_generator_config.yml",
                    "azure-output-filename": f"tmp_{FAKE.ean8()}.yml",
                },
            },
        }

    def test_replace_args_no_output_file(self):
        """Test replace args."""
        from nise.yaml_gen import STATIC_DIR

        self.yaml_file["ocp-on-aws"]["ocp"].pop("ocp-output-filename")
        replace_args(self.args, self.yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
        self.assertEqual(self.args.output_file_name, "ocp-on-aws_ocp.yml")
        self.assertEqual(self.args.template_file_name, os.path.join(STATIC_DIR, "ocp_static_data.yml.j2"))

    def test_replace_args_not_default(self):
        """Test replace args."""
        self.args.default = False
        replace_args(self.args, self.yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
        self.assertEqual(self.args.output_file_name, self.yaml_file["ocp-on-aws"]["ocp"].get("ocp-output-filename"))
        self.assertEqual(self.args.template_file_name, "ocp_static_data.yml.j2")

    def test_replace_args_not_default_no_template(self):
        """Test replace args."""
        from nise.yaml_gen import STATIC_DIR

        self.args.default = False
        self.yaml_file["ocp-on-aws"]["ocp"].pop("ocp-template")
        replace_args(self.args, self.yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
        self.assertEqual(self.args.output_file_name, self.yaml_file["ocp-on-aws"]["ocp"].get("ocp-output-filename"))
        self.assertEqual(self.args.template_file_name, os.path.join(STATIC_DIR, "ocp_static_data.yml.j2"))

    def test_replace_args_not_default_no_config(self):
        """Test replace args."""
        self.args.default = False
        self.yaml_file["ocp-on-aws"]["ocp"].pop("ocp-gen-config")
        replace_args(self.args, self.yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
        self.assertEqual(self.args.output_file_name, self.yaml_file["ocp-on-aws"]["ocp"].get("ocp-output-filename"))
        self.assertIsNone(self.args.config_file_name)

    def test_replace_args_no_yaml(self):
        """Test replace args."""
        self.yaml_file["ocp-on-aws"].pop("ocp")
        with self.assertRaises(KeyError):
            replace_args(self.args, self.yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")

    def test_cache(self):  # noqa: C901
        """Test that labels and resource_ids are unique between ocp-on-aws and ocp-on-azure - LONG TEST."""

        def listify(keys, index):
            """Convert tuple index to list."""
            return [key[index] for key in keys]

        try:
            replace_args(self.args, self.yaml_file.get("ocp-on-aws").get("ocp"), "ocp", "ocp-on-aws")
            self.args.config_file_name = None
            config = get_validated_config(self.ocp, self.args)
            config.max_nodes = 1000
            data = run_generator(self.ocp, self.args, config)
            id_labels_1 = get_resourceid_and_tags(data)
        finally:
            os.remove(self.yaml_file["ocp-on-aws"]["ocp"]["ocp-output-filename"])

        try:
            replace_args(self.args, self.yaml_file.get("ocp-on-azure").get("ocp"), "ocp", "ocp-on-azure")
            self.args.config_file_name = None
            config = get_validated_config(self.ocp, self.args)
            config.max_nodes = 1000
            data = run_generator(self.ocp, self.args, config)
            id_labels_2 = get_resourceid_and_tags(data)
        finally:
            os.remove(self.yaml_file["ocp-on-azure"]["ocp"]["ocp-output-filename"])

        id_labels_1_resource_ids = listify(id_labels_1.keys(), 0)
        id_labels_2_resource_ids = listify(id_labels_2.keys(), 0)
        for res_id in id_labels_1_resource_ids:
            self.assertNotIn(res_id, id_labels_2_resource_ids)

        id_labels_1_node_names = listify(id_labels_1.keys(), 1)
        id_labels_2_node_names = listify(id_labels_2.keys(), 1)
        for node in id_labels_1_node_names:
            self.assertNotIn(node, id_labels_2_node_names)

        for namespace_values in id_labels_1.values():
            for values in namespace_values:
                for value in values:
                    for namespace_values2 in id_labels_2.values():
                        for values2 in namespace_values2:
                            self.assertNotIn(value, values2)

    def test_process_template(self):
        """Test that process template produces 4 files."""
        with patch("nise.__main__.load_yaml_file", return_value=self.yaml_file):
            with patch("nise.yaml_generators.ocp_on_cloud.generator.replace_args", side_effect=mock_replace_args):
                self.yg.process_template(self.args)
        self.assertTrue(os.path.exists(self.yaml_file["ocp-on-azure"]["ocp"]["ocp-output-filename"]))
        self.assertTrue(os.path.exists(self.yaml_file["ocp-on-azure"]["azure"]["azure-output-filename"]))
        self.assertTrue(os.path.exists(self.yaml_file["ocp-on-aws"]["ocp"]["ocp-output-filename"]))
        self.assertTrue(os.path.exists(self.yaml_file["ocp-on-aws"]["aws"]["aws-output-filename"]))

        os.remove(self.yaml_file["ocp-on-aws"]["ocp"]["ocp-output-filename"])
        os.remove(self.yaml_file["ocp-on-aws"]["aws"]["aws-output-filename"])
        os.remove(self.yaml_file["ocp-on-azure"]["ocp"]["ocp-output-filename"])
        os.remove(self.yaml_file["ocp-on-azure"]["azure"]["azure-output-filename"])
