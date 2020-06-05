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
# import argparse
import os
import shutil
from importlib import import_module
from unittest import TestCase

from nise.yaml_generators.ocp_on_cloud import generator


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

    # def test_cache(self):
    #     """Test that labels and resource_ids are unique between ocp-on-aws and ocp-on-azure."""
    #     args = argparse.Namespace()
    #     args.default = True
    #     args.provider = "ocp-on-cloud"
    #     yaml_file = {
    #         "ocp-on-aws": {
    #             "ocp": {
    #                 "ocp-template": "ocp_static_data.yml.j2",
    #                 "ocp-gen-config": "ocp_generator_config.yml",
    #                 "ocp-output-filename": "ocp-on-aws_ocp.yml",
    #             },
    #             "aws": {
    #                 "aws-template": "aws_static_data.yml.j2",
    #                 "aws-gen-config": "aws_generator_config.yml",
    #                 "aws-output-filename": "ocp-on-aws_aws.yml",
    #             },
    #         },
    #         "ocp-on-azure": {
    #             "ocp": {
    #                 "ocp-template": "ocp_static_data.yml.j2",
    #                 "ocp-gen-config": "ocp_generator_config.yml",
    #                 "ocp-output-filename": "ocp-on-azure_ocp.yml",
    #             },
    #             "azure": {
    #                 "azure-template": "azure_static_data.yml.j2",
    #                 "azure-gen-config": "azure_generator_config.yml",
    #                 "azure-output-filename": "ocp-on-azure_azure.yml",
    #             },
    #         },
    #     }
