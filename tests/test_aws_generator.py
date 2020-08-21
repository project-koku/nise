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
import os
import tempfile
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.aws import AWS_GENERATORS
from nise.generators.aws import DataTransferGenerator
from nise.generators.aws import EBSGenerator
from nise.generators.aws import EC2Generator
from nise.generators.aws import RDSGenerator
from nise.generators.aws import Route53Generator
from nise.generators.aws import S3Generator
from nise.generators.aws import VPCGenerator


def create_test_config(**kwargs):
    """Create a test config. Users should remove the file at the end of the test."""
    test_yaml = """
---
generators:
  - {generator}:
      start_date: {start_date}
      end_date: {end_date}
      resource_id: {resource_id}
      product_sku: {product_sku}
      product_code: {product_code}
      product_name: {product_name}
      product_family: {product_family}
      region: {region}
      rate: {rate}
      amount: {amount}
      instance_type:
        inst_type: '{instance_type[inst_type]}'
        vcpu: '{instance_type[vcpu]}'
        memory: '{instance_type[memory]}'
        storage: '{instance_type[storage]}'
        family: '{instance_type[family]}'
        cost: '{instance_type[cost]}'
        rate: '{instance_type[rate]}'
        desc: '{instance_type[desc]}'
      tags:
        {tags[key]}: {tags[value]}
      payer_account: {payer_account}
      usage_accounts:
        - {usage_accounts[0]}
        - {usage_accounts[1]}
        - {usage_accounts[2]}
        - {usage_accounts[3]}
        - {usage_accounts[4]}
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
        self.test_config_kwargs = {
            "generator": None,
            "start_date": self.now - (2 * self.one_hour),
            "end_date": self.now,
            "resource_id": self.fake.word(),
            "product_sku": self.fake.word(),
            "product_code": self.fake.word(),
            "product_name": self.fake.word(),
            "tags": {"key": self.fake.word(), "value": self.fake.word()},
            "payer_account": self.payer_account,
            "usage_accounts": self.usage_accounts,
            "region": self.fake.word(),
        }

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator("invalid", self.now)

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator(self.now, "invalid")

    def test_set_hours_compared_dates(self):
        """Test that the start date must be less than the end date."""
        hour_ago = self.now - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator(self.now, hour_ago)

    def test_set_hours(self):
        """Test that a valid list of hours are returned."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                expected = [
                    {"start": two_hours_ago, "end": two_hours_ago + self.one_hour},
                    {"start": two_hours_ago + self.one_hour, "end": two_hours_ago + self.one_hour + self.one_hour},
                ]
                self.assertEqual(generator.hours, expected)

    def test_timestamp_none(self):
        """Test that the timestamp method fails with None."""
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator.timestamp(None)

    def test_timestamp_invalid(self):
        """Test that the timestamp method fails with an not a date."""
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                with self.assertRaises(ValueError):
                    TestGenerator.timestamp("invalid")

    def test_init_data_row(self):
        """Test the init data row method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                a_row = generator._init_data_row(two_hours_ago, self.now)
                self.assertIsInstance(a_row, dict)
                for col in generator.AWS_COLUMNS:
                    self.assertIsNotNone(a_row.get(col))

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row(None, self.now)

    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row(two_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row("invalid", self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                with self.assertRaises(ValueError):
                    generator._init_data_row(two_hours_ago, "invalid")

    def test_get_location(self):
        """Test the _get_location method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                location = generator._get_location()
                self.assertIsInstance(location, tuple)

        region = "us-west-1"
        for TestGenerator in AWS_GENERATORS:
            with self.subTest(generator=TestGenerator.__name__):
                generator = TestGenerator(two_hours_ago, self.now)
                location = generator._get_location(config={"region": region})
                self.assertIn(region, location)


class AWSGeneratorTestCase(TestCase):
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

        self.product_sku = 12345
        self.tags = {"key": self.fake.word(), "value": self.fake.word()}
        self.instance_type = {
            "inst_type": "1",
            "vcpu": "1",
            "memory": "1",
            "storage": "1",
            "family": "1",
            "cost": "1",
            "rate": "1",
            "desc": self.fake.word(),
        }
        self.product_code = "AmazonEC2"
        self.product_name = "Amazon Elastic Compute Cloud"
        self.product_family = "DNS Query"
        self.resource_id = 12345
        self.amount = 1
        self.rate = 0.1
        self.two_hours_ago = (self.now - self.one_hour) - self.one_hour

        self.test_config_kwargs = {
            "generator": "EC2Generator",
            "start_date": self.now - (2 * self.one_hour),
            "end_date": self.now,
            "resource_id": self.resource_id,
            "product_sku": self.product_sku,
            "product_code": self.product_code,
            "product_name": self.product_name,
            "product_family": self.product_family,
            "tags": self.tags,
            "payer_account": self.payer_account,
            "usage_accounts": self.usage_accounts,
            "region": self.fake.word(),
            "rate": self.rate,
            "amount": self.amount,
            "instance_type": self.instance_type,
        }

    def test_tag_cols(self):
        """Test new tag gets assigned to AWS_COLUMNS."""
        key = "resourceTags/user:new-key"
        test_args = self.test_config_kwargs
        test_args["tags"]["key"] = key
        test_config = create_test_config(**test_args)
        generator = EC2Generator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertIn(key, generator.AWS_COLUMNS)
        self.assertNotIn("key-that-has-not-been-added", generator.AWS_COLUMNS)
        os.remove(test_config)

    def test_unknown_location(self):
        """Test that an unknown location doesn't result in stack trace."""
        test_args = self.test_config_kwargs
        test_args["region"] = "Bad Result"
        key = "resourceTags/user:new-key"
        test_args["tags"]["key"] = key
        test_config = create_test_config(**test_args)
        generator = DataTransferGenerator(self.two_hours_ago, self.now)
        self.assertIn(key, generator.AWS_COLUMNS)
        self.assertNotIn("key-that-has-not-been-added", generator.AWS_COLUMNS)
        os.remove(test_config)


class TestRDSGenerator(AWSGeneratorTestCase):
    """Tests for the RDS Generator type."""

    def test_init_no_attributes(self):
        """Test the init wihout attributes."""
        generator = RDSGenerator(self.two_hours_ago, self.now)
        self.assertIsNotNone(generator.config[0].get("product_sku"))
        self.assertIsNotNone(generator.config[0].get("resource_id"))
        self.assertIsNotNone(generator.config[0].get("instance_type"))

    def test_init_with_attributes(self):
        """Test the unique init options for RDS."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "RDSGenerator"
        test_config = create_test_config(**test_args)
        generator = RDSGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("resource_id"), self.resource_id)
        self.assertEqual(tuple(generator.config[0].get("instance_type").values()), tuple(self.instance_type.values()))
        os.remove(test_config)

    def test_update_data(self):
        """Test RDS specific update data method."""
        test_args = self.test_config_kwargs
        test_args["generator"] = "RDSGenerator"
        test_config = create_test_config(**test_args)
        generator = RDSGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["lineItem/ProductCode"], "AmazonRDS")
        self.assertEqual(row["lineItem/Operation"], "CreateDBInstance")
        self.assertEqual(row["product/ProductName"], "Amazon Relational Database Service")
        os.remove(test_config)

    def test_generate_data(self):
        """Test that the RDS generate_data method works."""
        generator = RDSGenerator(self.two_hours_ago, self.now)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestDataTransferGenerator(AWSGeneratorTestCase):
    """Tests for the Data Transfer Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "DataTransferGenerator"
        test_config = create_test_config(**test_args)
        generator = DataTransferGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_code"), self.product_code)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("resource_id"), self.resource_id)
        self.assertEqual(generator.config[0].get("amount"), self.amount)
        self.assertEqual(generator.config[0].get("rate"), self.rate)
        os.remove(test_config)

    def test_update_data(self):
        """Test Data Transfer specific update data method."""
        generator = DataTransferGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["product/servicecode"], "AWSDataTransfer")
        self.assertEqual(row["product/productFamily"], "Data Transfer")


class TestEBSGenerator(AWSGeneratorTestCase):
    """Tests for the EBS Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "EBSGenerator"
        test_config = create_test_config(**test_args)
        generator = EBSGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("resource_id"), self.resource_id)
        self.assertEqual(generator.config[0].get("amount"), self.amount)
        self.assertEqual(generator.config[0].get("rate"), self.rate)
        os.remove(test_config)

    def test_update_data(self):
        """Test EBS specific update data method."""
        generator = EBSGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["product/servicecode"], "AmazonEC2")
        self.assertEqual(row["product/productFamily"], "Storage")
        self.assertEqual(row["lineItem/Operation"], "CreateVolume")

    def test_generate_data(self):
        """Test that the EBS generate_data method works."""
        generator = EBSGenerator(self.two_hours_ago, self.now)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestEC2Generator(AWSGeneratorTestCase):
    """Tests for the EBS Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "EC2Generator"
        test_config = create_test_config(**test_args)
        generator = EC2Generator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("resource_id"), self.resource_id)
        self.assertEqual(tuple(generator.config[0].get("instance_type").values()), tuple(self.instance_type.values()))
        os.remove(test_config)

    def test_update_data(self):
        """Test EBS specific update data method."""
        generator = EC2Generator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["product/servicecode"], "AmazonEC2")
        self.assertEqual(row["product/productFamily"], "Compute Instance")
        self.assertEqual(row["lineItem/Operation"], "RunInstances")

    def test_generate_data(self):
        """Test that the EBS generate_data method works."""
        generator = EC2Generator(self.two_hours_ago, self.now)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestRoute53Generator(AWSGeneratorTestCase):
    """Tests for the Route53 Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "Route53Generator"
        test_config = create_test_config(**test_args)
        generator = Route53Generator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("product_family"), self.product_family)
        os.remove(test_config)

    def test_update_data(self):
        """Test Route53 specific update data method."""
        generator = Route53Generator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["product/servicecode"], "AmazonRoute53")
        self.assertIn(row["product/productFamily"], ["DNS Query", "DNS Zone"])
        self.assertEqual(row["lineItem/ProductCode"], "AmazonRoute53")

    def test_generate_data(self):
        """Test that the Route53 generate_data method works."""
        generator = Route53Generator(self.two_hours_ago, self.now)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestS3Generator(AWSGeneratorTestCase):
    """Tests for the S3 Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "S3Generator"
        test_config = create_test_config(**test_args)
        generator = S3Generator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("amount"), self.amount)
        self.assertEqual(generator.config[0].get("rate"), self.rate)
        os.remove(test_config)

    def test_update_data(self):
        """Test S3 specific update data method."""
        generator = S3Generator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["product/servicecode"], "AmazonS3")
        self.assertEqual(row["lineItem/Operation"], "GetObject")
        self.assertEqual(row["lineItem/ProductCode"], "AmazonS3")

    def test_generate_data(self):
        """Test that the S3 generate_data method works."""
        generator = S3Generator(self.two_hours_ago, self.now)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestVPCGenerator(AWSGeneratorTestCase):
    """Tests for the VPC Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "VPCGenerator"
        test_config = create_test_config(**test_args)
        generator = VPCGenerator(self.two_hours_ago, self.now, user_config=test_config)
        self.assertEqual(generator.config[0].get("product_sku"), self.product_sku)
        self.assertIn(self.tags["key"], generator.config[0].get("tags").keys())
        self.assertEqual(generator.config[0].get("resource_id"), self.resource_id)
        os.remove(test_config)

    def test_update_data(self):
        """Test VPC specific update data method."""
        generator = VPCGenerator(self.two_hours_ago, self.now)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now, **{"config": generator.config[0]})

        self.assertEqual(row["product/servicecode"], "AmazonVPC")
        self.assertEqual(row["lineItem/Operation"], "CreateVpnConnection")
        self.assertEqual(row["lineItem/ProductCode"], "AmazonVPC")

    def test_generate_data(self):
        """Test that the VPC generate_data method works."""
        generator = VPCGenerator(self.two_hours_ago, self.now)
        data = generator.generate_data()
        self.assertNotEqual(data, [])
