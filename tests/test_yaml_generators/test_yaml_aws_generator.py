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
import shutil
from importlib import import_module
from unittest import TestCase

from nise.yaml_generators.aws import generator
from nise.yaml_generators.aws.ec2_instance_types import INSTANCE_TYPES as EC2_INSTANCE_TYPES
from nise.yaml_generators.aws.rds_instance_types import INSTANCE_TYPES as RDS_INSTANCE_TYPES


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
GEN_FILE_DIR = os.path.dirname(os.path.abspath(generator.__file__))
CACHE_PATH = os.path.join(os.path.dirname(GEN_FILE_DIR), "__pycache__")


class AWSGeneratorTestCase(TestCase):
    """
    Base TestCase class, for AWS yaml gen.
    """

    @classmethod
    def setUpClass(cls):
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)

        cls.module = import_module("nise.yaml_generators.aws.generator")
        cls.yg = cls.module.AWSGenerator()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)

    def test_default_config(self):
        """Test default configuration."""
        dc = self.yg.default_config()
        self.assertTrue(isinstance(dc, self.module.dicta))
        self.assertTrue(self.yg.validate_config(dc))

    def test_config_validator(self):
        """Test config validation """
        dc = self.yg.default_config()
        self.assertTrue(self.yg.validate_config(dc))
        with self.assertRaises(TypeError):
            dc.start_date = ""
            self.assertFalse(self.yg.validate_config(dc))

    def test_generate_tags(self):
        """
        Test label string generator
        """
        dc = self.yg.default_config()
        for key in self.module.RESOURCE_TAG_COLS.keys():
            with self.subTest(key=key):
                tags = self.module.generate_tags(key, dc)
                self.assertEqual(len(tags), len(self.module.RESOURCE_TAG_COLS[key]))
                for tag in tags:
                    self.assertTrue(tag.get("key") in self.module.RESOURCE_TAG_COLS[key])

    def test_build_data(self):  # noqa: C901
        """
        Test create data static and random
        """

        def check_exact(val, config_val, **kwargs):
            return val == config_val

        def check_range(val, config_val, v_min=1):
            return v_min <= val <= config_val

        def validate_data(data, config, check_func):
            common_keys = ["start_date", "end_date", "resource_id", "product_sku", "tags"]
            data_transfer_gens_keys = sorted(common_keys + ["rate", "amount"])
            ebs_gens_keys = sorted(common_keys + ["rate", "amount"])
            ec2_gens_keys = sorted(common_keys + ["processor_arch", "region", "instance_type"])
            rds_gens_keys = sorted(common_keys + ["processor_arch", "region", "instance_type"])
            route53_gens_keys = sorted(common_keys + ["product_family"])
            s3_gens_keys = sorted(common_keys + ["rate", "amount"])
            vpc_gens_keys = sorted(common_keys)

            self.assertTrue(isinstance(data, self.module.dicta))

            self.assertTrue(check_func(len(data.data_transfer_gens), config.max_data_transfer_gens))
            self.assertTrue(check_func(len(data.ebs_gens), config.max_ebs_gens))
            self.assertTrue(check_func(len(data.ec2_gens), config.max_ec2_gens))
            self.assertTrue(check_func(len(data.rds_gens), config.max_rds_gens))
            self.assertTrue(check_func(len(data.route53_gens), config.max_route53_gens))
            self.assertTrue(check_func(len(data.s3_gens), config.max_s3_gens))
            self.assertTrue(check_func(len(data.vpc_gens), config.max_vpc_gens))
            self.assertTrue(check_func(len(data.users), config.max_users))

            for gen in data.data_transfer_gens:
                self.assertEqual(sorted(gen.keys()), data_transfer_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)
            for gen in data.ebs_gens:
                self.assertEqual(sorted(gen.keys()), ebs_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)

            list_inst_types = [d.get("inst_type") for d in EC2_INSTANCE_TYPES]
            for gen in data.ec2_gens:
                self.assertEqual(sorted(gen.keys()), ec2_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)
                self.assertTrue(gen.instance_type.get("inst_type") in list_inst_types)

            list_inst_types = [d.get("inst_type") for d in RDS_INSTANCE_TYPES]
            for gen in data.rds_gens:
                self.assertEqual(sorted(gen.keys()), rds_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)
                self.assertTrue(gen.instance_type.get("inst_type") in list_inst_types)

            for gen in data.route53_gens:
                self.assertEqual(sorted(gen.keys()), route53_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)

            for gen in data.s3_gens:
                self.assertEqual(sorted(gen.keys()), s3_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)

            for gen in data.vpc_gens:
                self.assertEqual(sorted(gen.keys()), vpc_gens_keys)
                self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))
                self.assertTrue(gen.resource_id is not None)

        dc = self.yg.default_config()

        data = self.yg.build_data(dc, False)
        validate_data(data, dc, check_exact)

        data = self.yg.build_data(dc, True)
        validate_data(data, dc, check_range)
