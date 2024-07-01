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
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.azure import AZURE_COLUMNS_V2_RESOURCE_GROUP
from nise.generators.azure import AZURE_COLUMNS_V2_SUBSCRIPTION
from nise.generators.azure import AzureGenerator
from nise.generators.azure import BandwidthGenerator
from nise.generators.azure import DTGenerator
from nise.generators.azure import SQLGenerator
from nise.generators.azure import StorageGenerator
from nise.generators.azure import VMGenerator
from nise.generators.azure import VNGenerator
from nise.report import _generate_azure_account_info

# from nise.generators.generator import AbstractGenerator

CONSUMED_SERVICE = ["Microsoft.Sql", "Microsoft.Storage", "Microsoft.Compute", "Microsoft.Network"]


class TestGenerator(AzureGenerator):
    def _update_data(self, row, start, end):
        return None

    def _generate_daily_data(self):
        return []

    def generate_data(self, report_type=None):
        return []


class AbstractGeneratorTestCase(TestCase):
    """
    TestCase class for Abstract Generator
    """

    def setUp(self):
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.account_info = _generate_azure_account_info()
        self.payer_account = self.account_info.get("subscription_guid")
        self.resource_group_attribute = {"resource_group": True}
        self.currency = "USD"

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        with self.assertRaises(ValueError):
            TestGenerator("invalid", self.now, self.currency, self.account_info)

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        with self.assertRaises(ValueError):
            TestGenerator(self.now, "invalid", self.currency, self.account_info)

    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        with self.assertRaises(ValueError):
            TestGenerator(None, self.now, self.currency, self.account_info)

    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        with self.assertRaises(ValueError):
            TestGenerator(self.now, None, self.currency, self.account_info)

    def test_set_hours_compared_dates(self):
        """Test that the start date must be less than the end date."""
        hour_ago = self.now - self.one_hour
        with self.assertRaises(ValueError):
            TestGenerator(self.now, hour_ago, self.currency, self.account_info)

    def test_set_hours(self):
        """Test that a valid list of hours are returned."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generators = [
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info),
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, self.resource_group_attribute),
        ]
        expected = [
            {"start": two_hours_ago, "end": two_hours_ago + self.one_hour},
            {"start": two_hours_ago + self.one_hour, "end": two_hours_ago + self.one_hour + self.one_hour},
        ]
        for generator in generators:
            self.assertEqual(generator.hours, expected)

    def test_init_data_row(self):
        """Test the init data row method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generators = [
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info),
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, self.resource_group_attribute),
        ]
        for generator in generators:
            columns = generator.azure_columns
            self.assertIn(columns, [AZURE_COLUMNS_V2_SUBSCRIPTION, AZURE_COLUMNS_V2_RESOURCE_GROUP])
            a_row = generator._init_data_row(two_hours_ago, self.now)
            self.assertIsInstance(a_row, dict)
            for col in columns:
                self.assertIsNotNone(a_row.get(col))

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generators = [
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info),
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, self.resource_group_attribute),
        ]
        for generator in generators:
            with self.assertRaises(ValueError):
                generator._init_data_row(None, self.now)

    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generators = [
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info),
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, self.resource_group_attribute),
        ]
        for generator in generators:
            with self.assertRaises(ValueError):
                generator._init_data_row(two_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generators = [
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info),
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, self.resource_group_attribute),
        ]
        for generator in generators:
            with self.assertRaises(ValueError):
                generator._init_data_row("invalid", self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generators = [
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info),
            TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, self.resource_group_attribute),
        ]
        for generator in generators:
            with self.assertRaises(ValueError):
                generator._init_data_row(two_hours_ago, "invalid")

    def test_get_location(self):
        """Test the _get_location method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now, self.currency, self.account_info)
        location = generator._get_location()
        self.assertIsInstance(location, tuple)

        attributes = {}
        attributes["resource_location"] = "US East"
        generator = TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, attributes)
        location = generator._get_location()
        self.assertIn("US East", location)

    def test_get_additional_info(self):
        """Test the _get_additional_info method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now, self.currency, self.account_info)
        add_info = generator._get_additional_info()
        self.assertIsNone(add_info)

        attributes = {}
        attributes["additional_info"] = {"VCPU": "1"}
        generator = TestGenerator(two_hours_ago, self.now, self.currency, self.account_info, attributes)
        add_info = generator._get_additional_info()
        self.assertIn("VCPU", add_info)


class AzureGeneratorTestCase(TestCase):
    """Test Base for specific generator classes."""

    def setUp(self):
        """Set up each test."""
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.account_info = _generate_azure_account_info()
        self.payer_account = self.account_info.get("subscription_guid")

        self.tags = {"key": "value"}
        self.service_name = "Storage"
        self.tags = {"key": "value"}
        self.instance_id = "subscriptions/38f1d748-3ac7-4b7f-a5ae-8b5ff16db82c/resourceGroups/hccm/providers/Microsoft.Storage/storageAccount/mysa1"  # noqa: E501
        self.meter_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        self.usage_quantity = 1
        self.resource_rate = 0.1
        self.pre_tax_cost = 20
        self.currency = "USD"
        self.attributes = {
            "tags": self.tags,
            "instance_id": self.instance_id,
            "meter_id": self.meter_id,
            "usage_quantity": self.usage_quantity,
            "resource_rate": self.resource_rate,
            "pre_tax_cost": self.pre_tax_cost,
        }
        self.attributes_v2 = {
            "tags": self.tags,
            "instance_id": self.instance_id,
            "meter_id": self.meter_id,
            "usage_quantity": self.usage_quantity,
            "resource_rate": self.resource_rate,
            "pre_tax_cost": self.pre_tax_cost,
            "resource_group": True,
        }
        self.two_hours_ago = (self.now - self.one_hour) - self.one_hour


class TestBandwidthGenerator(AzureGeneratorTestCase):
    """Tests for the Bandwidth Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = BandwidthGenerator(
            self.two_hours_ago, self.now, self.currency, self.account_info, attributes={"empty": "dictionary"}
        )
        self.assertEqual(generator._service_name, "Bandwidth")
        self.assertIsNone(generator._service_tier)

    def test_init_with_attributes(self):
        """Test the unique init options for Bandwidth."""
        default_generators = [
            BandwidthGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            BandwidthGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            self.assertEqual(generator._service_name, "Bandwidth")
            self.assertEqual(generator._meter_id, self.meter_id)
            self.assertEqual(generator._tags, self.tags)
            self.assertEqual(generator._usage_quantity, self.usage_quantity)
            self.assertEqual(generator._resource_rate, self.resource_rate)
            self.assertEqual(generator._pre_tax_cost, self.pre_tax_cost)

    def test_update_data(self):
        """Test that row is updated."""
        default_generators = [
            BandwidthGenerator(self.two_hours_ago, self.now, self.account_info, self.attributes),
            BandwidthGenerator(self.two_hours_ago, self.now, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            start_row = {}
            row = generator._update_data(start_row, self.two_hours_ago, self.now)
            self.assertIn(row["ConsumedService"], CONSUMED_SERVICE)


class TestStorageGenerator(AzureGeneratorTestCase):
    """Tests for the Storage Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = StorageGenerator(
            self.two_hours_ago, self.now, self.currency, self.account_info, attributes={"empty": "dictionary"}
        )
        self.assertEqual(generator._service_name, "Storage")
        self.assertIsNone(generator._service_tier)

    def test_init_with_attributes(self):
        """Test the unique init options for Storage."""
        default_generators = [
            StorageGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            StorageGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            self.assertEqual(generator._service_name, "Storage")
            self.assertEqual(generator._meter_id, self.meter_id)
            self.assertEqual(generator._tags, self.tags)
            self.assertEqual(generator._usage_quantity, self.usage_quantity)
            self.assertEqual(generator._resource_rate, self.resource_rate)
            self.assertEqual(generator._pre_tax_cost, self.pre_tax_cost)

    def test_update_data(self):
        """Test that row is updated."""
        default_generators = [
            StorageGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            StorageGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            start_row = {}
            row = generator._update_data(start_row, self.two_hours_ago, self.now)
            self.assertEqual(row["ConsumedService"], "Microsoft.Storage")
            if generator.azure_columns == AZURE_COLUMNS_V2_SUBSCRIPTION:
                self.assertEqual(row["SubscriptionId"], self.payer_account)
            else:
                self.assertEqual(row["SubscriptionGuid"], self.payer_account)


class TestSQLGenerator(AzureGeneratorTestCase):
    """Tests for the SQL db Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = SQLGenerator(
            self.two_hours_ago, self.now, self.currency, self.account_info, attributes={"empty": "dictionary"}
        )
        self.assertEqual(generator._service_name, "SQL Database")
        self.assertIsNone(generator._service_tier)

    def test_init_with_attributes(self):
        """Test the unique init options for SQL db."""
        default_generators = [
            SQLGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            SQLGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            self.assertEqual(generator._service_name, "SQL Database")
            self.assertEqual(generator._meter_id, self.meter_id)
            self.assertEqual(generator._tags, self.tags)
            self.assertEqual(generator._usage_quantity, self.usage_quantity)
            self.assertEqual(generator._resource_rate, self.resource_rate)
            self.assertEqual(generator._pre_tax_cost, self.pre_tax_cost)

    def test_update_data(self):
        """Test that row is updated."""
        default_generators = [
            SQLGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            SQLGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            start_row = {}
            row = generator._update_data(start_row, self.two_hours_ago, self.now)
            self.assertEqual(row["ConsumedService"], "Microsoft.Sql")
            if generator.azure_columns == AZURE_COLUMNS_V2_SUBSCRIPTION:
                self.assertEqual(row["SubscriptionId"], self.payer_account)
            else:
                self.assertEqual(row["SubscriptionGuid"], self.payer_account)


class TestVMGenerator(AzureGeneratorTestCase):
    """Tests for the VM Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = VMGenerator(
            self.two_hours_ago, self.now, self.currency, self.account_info, attributes={"empty": "dictionary"}
        )
        self.assertEqual(generator._service_name, "Virtual Machines")
        self.assertIsNone(generator._service_tier)

    def test_init_with_attributes(self):
        """Test the unique init options for VM."""
        default_generators = [
            VMGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            VMGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            self.assertEqual(generator._service_name, "Virtual Machines")
            self.assertEqual(generator._meter_id, self.meter_id)
            self.assertEqual(generator._tags, self.tags)
            self.assertEqual(generator._usage_quantity, self.usage_quantity)
            self.assertEqual(generator._resource_rate, self.resource_rate)
            self.assertEqual(generator._pre_tax_cost, self.pre_tax_cost)

    def test_update_data(self):
        """Test that row is updated."""
        default_generators = [
            VMGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            VMGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            start_row = {}
            row = generator._update_data(start_row, self.two_hours_ago, self.now)
            self.assertEqual(row["ConsumedService"], "Microsoft.Compute")
            if generator.azure_columns == AZURE_COLUMNS_V2_SUBSCRIPTION:
                self.assertEqual(row["SubscriptionId"], self.payer_account)
            else:
                self.assertEqual(row["SubscriptionGuid"], self.payer_account)


class TestVNGenerator(AzureGeneratorTestCase):
    """Tests for the VM Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = VNGenerator(
            self.two_hours_ago, self.now, self.currency, self.account_info, attributes={"empty": "dictionary"}
        )
        self.assertEqual(generator._service_name, "Virtual Network")
        self.assertIsNone(generator._service_tier)

    def test_init_with_attributes(self):
        """Test the unique init options for VM."""
        default_generators = [
            VNGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            VNGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            self.assertEqual(generator._service_name, "Virtual Network")
            self.assertEqual(generator._meter_id, self.meter_id)
            self.assertEqual(generator._tags, self.tags)
            self.assertEqual(generator._usage_quantity, self.usage_quantity)
            self.assertEqual(generator._resource_rate, self.resource_rate)
            self.assertEqual(generator._pre_tax_cost, self.pre_tax_cost)

    def test_update_data(self):
        """Test that row is updated."""
        generator = VNGenerator(self.two_hours_ago, self.now, self.currency, self.account_info)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)
        self.assertEqual(row["ConsumedService"], "Microsoft.Network")

    def test_update_data_with_attributes(self):
        """Test that row is updated."""
        default_generators = [
            VNGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            VNGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            start_row = {}
            row = generator._update_data(start_row, self.two_hours_ago, self.now)
            self.assertEqual(row["Tags"], json.dumps(self.tags))
            if generator.azure_columns == AZURE_COLUMNS_V2_SUBSCRIPTION:
                self.assertEqual(row["SubscriptionId"], self.payer_account)
                self.assertEqual(row["ResourceId"], self.instance_id)
                self.assertEqual(row["BillingCurrency"], self.currency)
            else:
                self.assertEqual(row["SubscriptionGuid"], self.payer_account)
                self.assertEqual(row["BillingCurrencyCode"], self.currency)


class TestDTGenerator(AzureGeneratorTestCase):
    """Tests for the VM Generator type."""

    ADDITIONAL_INFO_KEYS = {"Standard Data Processed - Egress", "Standard Data Processed - Ingress"}

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = DTGenerator(
            self.two_hours_ago, self.now, self.currency, self.account_info, attributes={"empty": "dictionary"}
        )
        self.assertEqual(generator._service_name, "Virtual Network")

    def test_init_with_attributes(self):
        """Test the unique init options for VM."""
        default_generators = [
            DTGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes),
            DTGenerator(self.two_hours_ago, self.now, self.currency, self.account_info, self.attributes_v2),
        ]
        for generator in default_generators:
            self.assertEqual(generator._service_name, "Virtual Network")
            self.assertEqual(generator._meter_id, self.meter_id)
            self.assertEqual(generator._tags, self.tags)
            self.assertEqual(generator._usage_quantity, self.usage_quantity)
            self.assertEqual(generator._resource_rate, self.resource_rate)
            self.assertEqual(generator._pre_tax_cost, self.pre_tax_cost)

    def test_update_data(self):
        """Test that row is updated."""
        generator = DTGenerator(self.two_hours_ago, self.now, self.currency, self.account_info)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)
        self.assertEqual(row["ConsumedService"], "microsoft.compute")

    def test_update_data_with_attributes(self):
        """Test that row is updated."""
        directional_attributes = {"data_direction": "in"}
        directional_attributes.update(self.attributes)
        directional_attributes_v2 = {"data_direction": "in"}
        directional_attributes_v2.update(self.attributes_v2)
        default_generators = [
            DTGenerator(
                self.two_hours_ago,
                self.now,
                self.currency,
                self.account_info,
                directional_attributes,
            ),
            DTGenerator(
                self.two_hours_ago,
                self.now,
                self.currency,
                self.account_info,
                directional_attributes_v2,
            ),
        ]
        for generator in default_generators:
            start_row = {}
            row = generator._update_data(start_row, self.two_hours_ago, self.now)
            self.assertEqual(row["Tags"], json.dumps(self.tags))
            if generator.azure_columns == AZURE_COLUMNS_V2_SUBSCRIPTION:
                self.assertEqual(row["SubscriptionId"], self.payer_account)
            else:
                self.assertEqual(row["SubscriptionGuid"], self.payer_account)
