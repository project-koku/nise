#
# Copyright 2018 Red Hat, Inc.
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
import json
import os
import tempfile
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.azure import AZURE_COLUMNS
from nise.generators.azure import AZURE_GENERATORS
from nise.generators.azure import BandwidthGenerator
from nise.generators.azure import SQLGenerator
from nise.generators.azure import StorageGenerator
from nise.generators.azure import VMGenerator
from nise.generators.azure import VNGenerator

# from nise.generators.generator import AbstractGenerator

CONSUMED_SERVICE = ["Microsoft.Sql", "Microsoft.Storage", "Microsoft.Compute", "Microsoft.Network"]


def create_test_config(**kwargs):
    """Create a test config. Users should remove the file at the end of the test."""
    test_yaml = """
---
generators:
  - {generator}:
      start_date: {start_date}
      end_date: {end_date}
      instance_id: {instance_id}
      meter_id: {meter_id}
      usage_quantity: {usage_quantity}
      resource_rate: {resource_rate}
      pre_tax_cost: {pre_tax_cost}
      tags:
        {tags[key]}: {tags[value]}
"""

    _, tmp_filename = tempfile.mkstemp()
    with open(tmp_filename, "w+") as tmp_handle:
        tmp_handle.write(test_yaml.format(**kwargs))

    return tmp_filename


class AbstractGeneratorTestCase(TestCase):
    """
    TestCase class for Abstract Generator
    """

    def setUp(self):
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.payer_account = self.fake.ean(length=13)
        self.usage_accounts = (
            self.payer_account,
            self.fake.ean(length=13),
            self.fake.ean(length=13),
            self.fake.ean(length=13),
            self.fake.ean(length=13),
        )

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator("invalid", self.now)

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator(self.now, "invalid")

    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator(None, self.now)

    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator(self.now, None)

    def test_set_hours_compared_dates(self):
        """Test that the start date must be less than the end date."""
        hour_ago = self.now - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator(self.now, hour_ago)

    def test_set_hours(self):
        """Test that a valid list of hours are returned."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                expected = [
                    {"start": two_hours_ago, "end": two_hours_ago + self.one_hour},
                    {"start": two_hours_ago + self.one_hour, "end": two_hours_ago + self.one_hour + self.one_hour},
                ]
                self.assertEqual(generator.hours, expected)

    def test_init_data_row(self):
        """Test the init data row method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                a_row = generator._init_data_row(two_hours_ago, self.now)
                self.assertIsInstance(a_row, dict)
                for col in AZURE_COLUMNS:
                    self.assertIsNotNone(a_row.get(col))

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row(None, self.now)

    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row(two_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row("invalid", self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row(two_hours_ago, "invalid")

    def test_get_location(self):
        """Test the _get_location method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                location = generator._get_location()

                self.assertIsInstance(location, tuple)

        expected = "US East"
        for TestGenerator in AZURE_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                location = generator._get_location(config={"resource_location": expected})
                self.assertIn(expected, location)


class AzureGeneratorTestCase(TestCase):
    """Test Base for specific generator classes."""

    def setUp(self):
        """Set up each test."""
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.payer_account = self.fake.ean(length=13)
        self.usage_accounts = (
            self.payer_account,
            self.fake.ean(length=13),
            self.fake.ean(length=13),
            self.fake.ean(length=13),
            self.fake.ean(length=13),
        )

        self.tags = {"key": self.fake.word(), "value": self.fake.word()}
        self.service_name = "Storage"
        self.instance_id = "subscriptions/38f1d748-3ac7-4b7f-a5ae-8b5ff16db82c/resourceGroups/hccm/providers/Microsoft.Storage/storageAccount/mysa1"  # noqa: E501
        self.meter_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        self.usage_quantity = 1
        self.resource_rate = 0.1
        self.pre_tax_cost = 20
        self.test_config_kwargs = {
            "generator": "VMGenerator",
            "start_date": self.now - self.one_hour * 2,
            "end_date": self.now,
            "tags": self.tags,
            "instance_id": self.instance_id,
            "meter_id": self.meter_id,
            "usage_quantity": self.usage_quantity,
            "resource_rate": self.resource_rate,
            "pre_tax_cost": self.pre_tax_cost,
        }
        self.two_hours_ago = (self.now - self.one_hour) - self.one_hour


class TestBandwidthGenerator(AzureGeneratorTestCase):
    """Tests for the Bandwidth Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = BandwidthGenerator(self.two_hours_ago, self.now)
        self.assertIsNotNone(generator.config[0].get("instance_id"))
        self.assertIsNotNone(generator.config[0].get("meter_id"))
        self.assertIsNotNone(generator.config[0].get("resource_location"))
        self.assertIsNotNone(generator.config[0].get("resource_rate"))
        self.assertIsNotNone(generator.config[0].get("usage_quantity"))

    def test_init_with_attributes(self):
        """Test the unique init options for Bandwidth."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "BandwidthGenerator"
        test_config = create_test_config(**test_args)
        generator = BandwidthGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("instance_id"), self.instance_id)
        self.assertEqual(generator.config[0].get("meter_id"), self.meter_id)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("usage_quantity"), self.usage_quantity)
        self.assertEqual(generator.config[0].get("resource_rate"), self.resource_rate)
        self.assertEqual(generator.config[0].get("pre_tax_cost"), self.pre_tax_cost)
        os.remove(test_config)

    def test_update_data(self):
        """Test that row is updated."""
        generator = BandwidthGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, config=self.test_config_kwargs)
        self.assertIn(row["ConsumedService"], CONSUMED_SERVICE)


class TestStorageGenerator(AzureGeneratorTestCase):
    """Tests for the Storage Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = StorageGenerator(self.two_hours_ago, self.now)
        self.assertIsNotNone(generator.config[0].get("instance_id"))
        self.assertIsNotNone(generator.config[0].get("meter_id"))
        self.assertIsNotNone(generator.config[0].get("resource_location"))
        self.assertIsNotNone(generator.config[0].get("resource_rate"))
        self.assertIsNotNone(generator.config[0].get("usage_quantity"))

    def test_init_with_attributes(self):
        """Test the unique init options for Storage."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "StorageGenerator"
        test_config = create_test_config(**test_args)
        generator = StorageGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("instance_id"), self.instance_id)
        self.assertEqual(generator.config[0].get("meter_id"), self.meter_id)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("usage_quantity"), self.usage_quantity)
        self.assertEqual(generator.config[0].get("resource_rate"), self.resource_rate)
        self.assertEqual(generator.config[0].get("pre_tax_cost"), self.pre_tax_cost)
        os.remove(test_config)

    def test_update_data(self):
        """Test that row is updated."""
        generator = StorageGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, config=self.test_config_kwargs)
        self.assertEqual(row["ConsumedService"], "Microsoft.Storage")
        self.assertEqual(row["ResourceType"], "Microsoft.Storage/storageAccounts")


class TestSQLGenerator(AzureGeneratorTestCase):
    """Tests for the SQL db Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = SQLGenerator(self.two_hours_ago, self.now)
        self.assertIsNotNone(generator.config[0].get("instance_id"))
        self.assertIsNotNone(generator.config[0].get("meter_id"))
        self.assertIsNotNone(generator.config[0].get("resource_location"))
        self.assertIsNotNone(generator.config[0].get("resource_rate"))
        self.assertIsNotNone(generator.config[0].get("usage_quantity"))

    def test_init_with_attributes(self):
        """Test the unique init options for SQL db."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "SQLGenerator"
        test_config = create_test_config(**test_args)
        generator = SQLGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("instance_id"), self.instance_id)
        self.assertEqual(generator.config[0].get("meter_id"), self.meter_id)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("usage_quantity"), self.usage_quantity)
        self.assertEqual(generator.config[0].get("resource_rate"), self.resource_rate)
        self.assertEqual(generator.config[0].get("pre_tax_cost"), self.pre_tax_cost)
        os.remove(test_config)

    def test_update_data(self):
        """Test that row is updated."""
        generator = SQLGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, config=self.test_config_kwargs)
        self.assertEqual(row["ConsumedService"], "Microsoft.Sql")
        self.assertEqual(row["ResourceType"], "Microsoft.Sql/servers")


class TestVMGenerator(AzureGeneratorTestCase):
    """Tests for the VM Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = VMGenerator(self.two_hours_ago, self.now)
        self.assertIsNotNone(generator.config[0].get("instance_id"))
        self.assertIsNotNone(generator.config[0].get("meter_id"))
        self.assertIsNotNone(generator.config[0].get("resource_location"))
        self.assertIsNotNone(generator.config[0].get("resource_rate"))
        self.assertIsNotNone(generator.config[0].get("usage_quantity"))

    def test_init_with_attributes(self):
        """Test the unique init options for VM."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "VMGenerator"
        test_config = create_test_config(**test_args)
        generator = VMGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("instance_id"), self.instance_id)
        self.assertEqual(generator.config[0].get("meter_id"), self.meter_id)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("usage_quantity"), self.usage_quantity)
        self.assertEqual(generator.config[0].get("resource_rate"), self.resource_rate)
        self.assertEqual(generator.config[0].get("pre_tax_cost"), self.pre_tax_cost)
        os.remove(test_config)

    def test_update_data(self):
        """Test that row is updated."""
        generator = VMGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, config=self.test_config_kwargs)
        self.assertEqual(row["ConsumedService"], "Microsoft.Compute")
        self.assertEqual(row["ResourceType"], "Microsoft.Compute/virtualMachines")


class TestVNGenerator(AzureGeneratorTestCase):
    """Tests for the VM Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = VNGenerator(self.two_hours_ago, self.now, self.payer_account)
        self.assertIsNotNone(generator.config[0].get("instance_id"))
        self.assertIsNotNone(generator.config[0].get("meter_id"))
        self.assertIsNotNone(generator.config[0].get("resource_location"))
        self.assertIsNotNone(generator.config[0].get("resource_rate"))
        self.assertIsNotNone(generator.config[0].get("usage_quantity"))

    def test_init_with_attributes(self):
        """Test the unique init options for VM."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "VNGenerator"
        test_config = create_test_config(**test_args)
        generator = VNGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("instance_id"), self.instance_id)
        self.assertEqual(generator.config[0].get("meter_id"), self.meter_id)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("usage_quantity"), self.usage_quantity)
        self.assertEqual(generator.config[0].get("resource_rate"), self.resource_rate)
        self.assertEqual(generator.config[0].get("pre_tax_cost"), self.pre_tax_cost)
        os.remove(test_config)

    def test_update_data(self):
        """Test that row is updated."""
        generator = VNGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, config=self.test_config_kwargs)
        self.assertEqual(row["ConsumedService"], "Microsoft.Network")
        self.assertEqual(row["ResourceType"], "Microsoft.Network/publicIPAddresses")
        self.assertEqual(row["InstanceId"], self.instance_id)
        self.assertEqual(row["Tags"], json.dumps(self.tags))
