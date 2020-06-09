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

from nise.yaml_generators.azure import generator


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
GEN_FILE_DIR = os.path.dirname(os.path.abspath(generator.__file__))
CACHE_PATH = os.path.join(os.path.dirname(GEN_FILE_DIR), "__pycache__")


class AzureGeneratorTestCase(TestCase):
    """
    Base TestCase class, for Azure yaml gen.
    """

    @classmethod
    def setUpClass(cls):
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)

        cls.module = import_module("nise.yaml_generators.azure.generator")
        cls.yg = cls.module.AzureGenerator()

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
        for key in self.module.TAG_KEYS.keys():
            with self.subTest(key=key):
                tags, _ = self.module.generate_tags_and_instance_id(key, dc)
                self.assertEqual(len(tags), len(self.module.TAG_KEYS[key]))
                for tag in tags:
                    self.assertTrue(tag.get("key") in self.module.TAG_KEYS[key])

    def test_build_data(self):  # noqa: C901
        """
        Test create data static and random
        """

        def check_exact(val, config_val, **kwargs):
            return val == config_val

        def check_range(val, config_val, v_min=0):
            return v_min <= val <= config_val

        def validate_data(data, config, check_func):
            keys = sorted(
                [
                    "end_date",
                    "instance_id",
                    "meter_id",
                    "pre_tax_cost",
                    "resource_location",
                    "resource_rate",
                    "start_date",
                    "tags",
                    "usage_quantity",
                ]
            )
            gens = ["bandwidth_gens", "sql_gens", "storage_gens", "vmachine_gens", "vnetwork_gens"]

            self.assertTrue(isinstance(data, self.module.dicta))

            for gen in gens:
                self.assertTrue(check_func(len(data.get(gen)), config.get(f"max_{gen}")))

                for gen in data.get(gen):
                    self.assertEqual(sorted(gen.keys()), keys)
                    self.assertTrue(isinstance(gen.start_date, str) and isinstance(gen.end_date, str))

        dc = self.yg.default_config()

        for boo in (True, False):
            check_func = check_range if boo else check_exact
            with self.subTest(random=boo):
                data = self.yg.build_data(dc, boo)
                validate_data(data, dc, check_func)
