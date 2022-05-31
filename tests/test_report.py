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
import base64
import calendar
import csv
import datetime
import json
import os
import re
import shutil
from tempfile import mkdtemp
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import faker
from dateutil.relativedelta import relativedelta
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS
from nise.generators.ocp.ocp_generator import OCP_REPORT_TYPE_TO_COLS
from nise.report import _convert_bytes
from nise.report import _create_generator_dates_from_yaml
from nise.report import _create_month_list
from nise.report import _generate_azure_filename
from nise.report import _get_generators
from nise.report import _get_jsonl_generators
from nise.report import _remove_files
from nise.report import _write_csv
from nise.report import _write_jsonl
from nise.report import _write_manifest
from nise.report import aws_create_marketplace_report
from nise.report import aws_create_report
from nise.report import azure_create_report
from nise.report import default_currency
from nise.report import gcp_create_report
from nise.report import gcp_route_file
from nise.report import oci_bucket_upload
from nise.report import oci_create_report
from nise.report import oci_route_file
from nise.report import ocp_create_report
from nise.report import ocp_route_file
from nise.report import post_payload_to_ingest_service
from nise.report import write_oci_file


fake = faker.Faker()


class MiscReportTestCase(TestCase):
    """
    TestCase class for report functions
    """

    def test_convert_bytes(self):
        """Test the _convert_bytes method."""
        expected = "5.0 GB"
        result = _convert_bytes(5368709120)
        self.assertEqual(expected, str(result))
        # The covert function can't handle a number outside of TB
        expected = None
        petabyte_value = 100000000000000000000
        result = _convert_bytes(petabyte_value)
        self.assertEqual(result, expected)

    def test_write_csv(self):
        """Test the writing of the CSV data."""
        temp_file = NamedTemporaryFile(mode="w", delete=False)
        headers = ["col1", "col2"]
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_csv(temp_file.name, data, headers)
        self.assertTrue(os.path.exists(temp_file.name))
        os.remove(temp_file.name)

    def test_write_jsonl(self):
        """Test the writing of the jsonl data."""
        temp_file = NamedTemporaryFile(mode="w", delete=False)
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_jsonl(temp_file.name, data)
        self.assertTrue(os.path.exists(temp_file.name))
        os.remove(temp_file.name)

    def test_remove_files(self):
        """Test to see if files are deleted."""
        temp_file = NamedTemporaryFile(mode="w", delete=False)
        headers = ["col1", "col2"]
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_csv(temp_file.name, data, headers)
        self.assertTrue(os.path.exists(temp_file.name))
        _remove_files([temp_file.name])
        self.assertFalse(os.path.exists(temp_file.name))

    def test_remove_file_not_found(self):
        """Test file not found exception."""
        self.assertRaises(FileNotFoundError, _remove_files, ["error"])

    def test_write_manifest(self):
        """Test the writing of the manifest data."""
        data = '[{"col1": "r1c1", "col2": "r1c2"},' '{"col1": "r2c1", "col2": "r2c2"}]'
        manifest_path = _write_manifest(data)
        self.assertTrue(os.path.exists(manifest_path))
        os.remove(manifest_path)

    def test_create_generator_for_dates_from_yaml(self):
        """Test helper function for generating dates."""
        month = {
            "name": "June",
            "start": datetime.datetime(2021, 6, 30, 0, 0),
            "end": datetime.datetime(2021, 6, 30, 23, 59),
        }

        attributes = {
            "start_date": datetime.datetime(2021, 6, 30, 0, 0),
            "end_date": datetime.datetime(2021, 7, 29, 15, 0),
        }

        start_date, end_date = _create_generator_dates_from_yaml(attributes, month)

        self.assertEqual(start_date, datetime.datetime(2021, 6, 30, 0, 0))
        self.assertEqual(end_date, datetime.datetime(2021, 6, 30, 23, 59))

    def test_create_generator_for_dates_from_yaml_middle_month(self):
        """Test helper function for generating dates verifying the middle month in a 3 month range."""
        month = {
            "name": "June",
            "start": datetime.datetime(2021, 6, 30, 0, 0),
            "end": datetime.datetime(2021, 6, 30, 23, 59),
        }

        attributes = {
            "start_date": datetime.datetime(2021, 5, 31, 0, 0),
            "end_date": datetime.datetime(2021, 7, 29, 15, 0),
        }

        start_date, end_date = _create_generator_dates_from_yaml(attributes, month)

        self.assertEqual(start_date, datetime.datetime(2021, 6, 30, 0, 0))
        self.assertEqual(end_date, datetime.datetime(2021, 6, 30, 23, 59))

    def test_create_month_list(self):
        """Test to create month lists."""
        test_matrix = [
            {
                "start_date": datetime.datetime(year=2018, month=1, day=15),
                "end_date": datetime.datetime(year=2018, month=1, day=30),
                "expected_list": [
                    {
                        "name": "January",
                        "start": datetime.datetime(year=2018, month=1, day=15),
                        "end": datetime.datetime(year=2018, month=1, day=30, hour=23, minute=59),
                    }
                ],
            },
            {
                "start_date": datetime.datetime(year=2018, month=11, day=15),
                "end_date": datetime.datetime(year=2019, month=1, day=5),
                "expected_list": [
                    {
                        "name": "November",
                        "start": datetime.datetime(year=2018, month=11, day=15),
                        "end": datetime.datetime(year=2018, month=12, day=1, hour=0, minute=0),
                    },
                    {
                        "name": "December",
                        "start": datetime.datetime(year=2018, month=12, day=1),
                        "end": datetime.datetime(year=2019, month=1, day=1, hour=0, minute=0),
                    },
                    {
                        "name": "January",
                        "start": datetime.datetime(year=2019, month=1, day=1),
                        "end": datetime.datetime(year=2019, month=1, day=5, hour=23, minute=59),
                    },
                ],
            },
            {
                "start_date": datetime.datetime(year=2021, month=6, day=1),
                "end_date": datetime.datetime(year=2021, month=7, day=29),
                "expected_list": [
                    {
                        "name": "June",
                        "start": datetime.datetime(year=2021, month=6, day=1),
                        "end": datetime.datetime(year=2021, month=7, day=1, hour=0, minute=0),
                    },
                    {
                        "name": "July",
                        "start": datetime.datetime(year=2021, month=7, day=1),
                        "end": datetime.datetime(year=2021, month=7, day=29, hour=23, minute=59),
                    },
                ],
            },
        ]

        for test_case in test_matrix:
            output = _create_month_list(test_case["start_date"], test_case["end_date"])
            self.assertCountEqual(output, test_case["expected_list"])

    def test_get_generators(self):
        """Test the _get_generators helper function."""
        generators = _get_generators(None)
        self.assertEqual(generators, [])

        generator_list = [{"EC2Generator": {"start_date": "2019-01-21", "end_date": "2019-01-22"}}]
        generators = _get_generators(generator_list)

        self.assertIsNotNone(generators)
        self.assertEqual(len(generators), 1)

        self.assertIsInstance(generators[0].get("attributes").get("start_date"), datetime.datetime)
        self.assertIsInstance(generators[0].get("attributes").get("end_date"), datetime.datetime)
        self.assertEqual(generators[0].get("attributes").get("start_date").month, 1)
        self.assertEqual(generators[0].get("attributes").get("start_date").day, 21)
        self.assertEqual(generators[0].get("attributes").get("start_date").year, 2019)
        self.assertEqual(generators[0].get("attributes").get("end_date").month, 1)
        self.assertEqual(generators[0].get("attributes").get("end_date").day, 22)
        self.assertEqual(generators[0].get("attributes").get("end_date").year, 2019)

    def test_get_jsonl_generators(self):
        """Test the _get_jsonl_generators helper function."""
        generators = _get_jsonl_generators(None)
        self.assertEqual(generators, [])

        generator_list = [{"ComputeEngineGenerator": {"start_date": "2019-01-21", "end_date": "2019-01-22"}}]
        generators = _get_jsonl_generators(generator_list)

        self.assertIsNotNone(generators)
        self.assertEqual(len(generators), 1)

        self.assertIsInstance(generators[0].get("attributes").get("start_date"), datetime.datetime)
        self.assertIsInstance(generators[0].get("attributes").get("end_date"), datetime.datetime)
        self.assertEqual(generators[0].get("attributes").get("start_date").month, 1)
        self.assertEqual(generators[0].get("attributes").get("start_date").day, 21)
        self.assertEqual(generators[0].get("attributes").get("start_date").year, 2019)
        self.assertEqual(generators[0].get("attributes").get("end_date").month, 1)
        self.assertEqual(generators[0].get("attributes").get("end_date").day, 22)
        self.assertEqual(generators[0].get("attributes").get("end_date").year, 2019)

    @patch.dict(os.environ, {"INSIGHTS_ACCOUNT_ID": "12345", "INSIGHTS_ORG_ID": "54321"})
    @patch("nise.report.requests.post")
    def test_post_payload_to_ingest_service_with_identity_header(self, mock_post):
        """Test that the identity header path is taken."""
        insights_account_id = os.environ.get("INSIGHTS_ACCOUNT_ID")
        insights_org_id = os.environ.get("INSIGHTS_ORG_ID")
        content_type = "application/vnd.redhat.hccm.tar+tgz"

        temp_file = NamedTemporaryFile(mode="w", delete=False)
        headers = ["col1", "col2"]
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_csv(temp_file.name, data, headers)

        insights_upload = {}
        header = {
            "identity": {
                "account_number": insights_account_id,
                "org_id": insights_org_id,
                "internal": {"org_id": insights_org_id},
                "type": content_type,
            }
        }
        headers = {"x-rh-identity": base64.b64encode(json.dumps(header).encode("UTF-8"))}

        post_payload_to_ingest_service(insights_upload, temp_file.name)
        self.assertEqual(mock_post.call_args[1].get("headers"), headers)
        self.assertNotIn("auth", mock_post.call_args[1])

    @patch.dict(os.environ, {"INSIGHTS_USER": "12345", "INSIGHTS_PASSWORD": "54321"})
    @patch("nise.report.requests.post")
    def test_post_payload_to_ingest_service_with_basic_auth(self, mock_post):
        """Test that the identity header path is taken."""
        insights_user = os.environ.get("INSIGHTS_USER")
        insights_password = os.environ.get("INSIGHTS_PASSWORD")

        temp_file = NamedTemporaryFile(mode="w", delete=False)
        headers = ["col1", "col2"]
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_csv(temp_file.name, data, headers)

        insights_upload = {}

        auth = (insights_user, insights_password)

        post_payload_to_ingest_service(insights_upload, temp_file.name)
        self.assertEqual(mock_post.call_args[1].get("auth"), auth)
        self.assertNotIn("headers", mock_post.call_args[1])

    def test_defaulting_currency(self):
        """Test that if no currency is provide in options or static it defaults to USD."""
        currency = None
        static_currency = None
        updated_currency = default_currency(currency, static_currency)
        self.assertEqual(updated_currency, "USD")

    def test_defaulting_to_static_currency(self):
        """Test that if no currency is provide in options it defaults to static."""
        currency = None
        static_currency = "NOK"
        updated_currency = default_currency(currency, static_currency)
        self.assertEqual(updated_currency, "NOK")

    def test_currency_option(self):
        """Test that if currency is provide in options it sets to that."""
        currency = "AUD"
        static_currency = "NOK"
        updated_currency = default_currency(currency, static_currency)
        self.assertEqual(updated_currency, "AUD")


class AWSReportTestCase(TestCase):
    """
    TestCase class for AWS report functions.
    """

    def test_aws_create_report_no_s3(self):
        """Test the aws report creation method no s3."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_report(
            {"start_date": yesterday, "end_date": now, "aws_report_name": "cur_report", "write_monthly": True}
        )

        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    @patch("nise.report.upload_to_s3")
    def test_aws_create_report_with_s3(self, mock_upload_to_s3):
        """Test the aws report creation method with s3."""
        mock_upload_to_s3.return_value = None
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": "my_bucket",
            "aws_report_name": "cur_report",
            "write_monthly": True,
        }
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    def test_aws_create_report_with_local_dir(self):
        """Test the aws report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "write_monthly": True,
        }
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_create_report_with_local_dir_report_prefix(self):
        """Test the aws report creation method with local directory and a report prefix."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "aws_prefix_name": "my_prefix",
            "write_monthly": True,
        }
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_create_report_finalize_report_copy(self):
        """Test that an aws finalized copy of a report file has an invoice id."""

        start_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.datetime.now().replace(day=5, hour=0, minute=0, second=0, microsecond=0)
        aws_create_report(
            {
                "start_date": start_date,
                "end_date": end_date,
                "aws_report_name": "cur_report",
                "aws_finalize_report": "copy",
                "write_monthly": True,
            }
        )
        month_output_file_name = "{}-{}-{}".format(
            calendar.month_name[start_date.month], start_date.year, "cur_report"
        )
        finalized_file_name = f"{month_output_file_name}-finalized"
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        expected_finalized_file = "{}/{}.csv".format(os.getcwd(), finalized_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        self.assertTrue(os.path.isfile(expected_finalized_file))
        with open(expected_month_output_file, "r") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertEqual(row["bill/InvoiceId"], "")

        with open(expected_finalized_file, "r") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertNotEqual(row["bill/InvoiceId"], "")

        os.remove(expected_month_output_file)
        os.remove(expected_finalized_file)

    def test_aws_create_report_finalize_report_overwrite(self):
        """Test that an aws report file has an invoice id."""
        start_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.datetime.now().replace(day=5, hour=0, minute=0, second=0, microsecond=0)
        aws_create_report(
            {
                "start_date": start_date,
                "end_date": end_date,
                "aws_report_name": "cur_report",
                "aws_finalize_report": "overwrite",
                "write_monthly": True,
            }
        )

        month_output_file_name = "{}-{}-{}".format(
            calendar.month_name[start_date.month], start_date.year, "cur_report"
        )
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))

        with open(expected_month_output_file, "r") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertNotEqual(row["bill/InvoiceId"], "")

        os.remove(expected_month_output_file)

    def test_aws_create_report_with_local_dir_static_generation(self):
        """Test the aws report creation method with local directory and static generation."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()

        static_aws_data = {
            "generators": [
                {
                    "EC2Generator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "processor_arch": "32-bit",
                        "resource_id": 55555555,
                        "product_sku": "VEAJHRNKTJZQ",
                        "region": "us-east-1a",
                        "tags": {"resourceTags/user:environment": "dev", "resourceTags/user:version": "alpha"},
                        "instance_type": {
                            "inst_type": "m5.large",
                            "vcpu": 2,
                            "memory": "8 GiB",
                            "storage": "EBS Only",
                            "family": "General Purpose",
                            "cost": 1.0,
                            "rate": 0.5,
                            "saving": 0.25,
                        },
                    }
                },
                {
                    "S3Generator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "product_sku": "VEAJHRNAAAAA",
                        "amount": 10,
                        "rate": 3,
                    }
                },
                {
                    "EBSGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "product_sku": "VEAJHRNBBBBB",
                        "amount": 10,
                        "rate": 3,
                        "resource_id": 12345678,
                    }
                },
                {
                    "DataTransferGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "product_sku": "VEAJHRNCCCCC",
                        "amount": 10,
                        "rate": 3,
                    }
                },
            ],
            "accounts": {"payer": 9999999999999, "user": [9999999999999]},
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "static_report_data": static_aws_data,
            "write_monthly": True,
        }
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_create_report_with_local_dir_static_generation_dates(self):
        """Test the aws report creation method with local directory and static generation with dates."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()

        static_aws_data = {
            "generators": [{"EC2Generator": {"start_date": str(now), "end_date": str(now)}}],
            "accounts": {"payer": 9999999999999, "user": [9999999999999]},
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "static_report_data": static_aws_data,
            "write_monthly": True,
        }
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_create_report_without_write_monthly(self):
        """Test that monthly file is not created by default."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_report({"start_date": yesterday, "end_date": now, "aws_report_name": "cur_report"})

        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertFalse(os.path.isfile(expected_month_output_file))

    def test_aws_create_report_with_local_dir_static_generation_multi_file(self):
        """Test the aws report creation method with local directory and static generation in multiple files."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()

        static_aws_data = {
            "generators": [
                {
                    "EC2Generator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "processor_arch": "32-bit",
                        "resource_id": 55555555,
                        "product_sku": "VEAJHRNKTJZQ",
                        "region": "us-east-1a",
                        "tags": {"resourceTags/user:environment": "dev", "resourceTags/user:version": "alpha"},
                        "instance_type": {
                            "inst_type": "m5.large",
                            "vcpu": 2,
                            "memory": "8 GiB",
                            "storage": "EBS Only",
                            "family": "General Purpose",
                            "cost": 1.0,
                            "rate": 0.5,
                            "saving": 0.25,
                        },
                    }
                },
                {
                    "S3Generator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "product_sku": "VEAJHRNAAAAA",
                        "amount": 10,
                        "rate": 3,
                    }
                },
                {
                    "EBSGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "product_sku": "VEAJHRNBBBBB",
                        "amount": 10,
                        "rate": 3,
                        "resource_id": 12345678,
                    }
                },
                {
                    "DataTransferGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "product_sku": "VEAJHRNCCCCC",
                        "amount": 10,
                        "rate": 3,
                    }
                },
            ],
            "accounts": {"payer": 9999999999999, "user": [9999999999999]},
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "static_report_data": static_aws_data,
            "row_limit": 20,
            "write_monthly": True,
        }
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file_1 = "{}/{}-1.csv".format(os.getcwd(), month_output_file_name)
        expected_month_output_file_2 = "{}/{}-2.csv".format(os.getcwd(), month_output_file_name)

        self.assertTrue(os.path.isfile(expected_month_output_file_1))
        self.assertTrue(os.path.isfile(expected_month_output_file_2))

        # cleanup any leftover files
        regex = re.compile(month_output_file_name)
        for _, _, files in os.walk("."):
            for fname in files:
                if regex.match(fname):
                    os.remove(fname)
        shutil.rmtree(local_bucket_path)


class AWSMarketplaceReportTestCase(TestCase):
    """
    TestCase class for AWS Marketplace report functions.
    """

    def test_aws_marketplace_create_report_no_s3(self):
        """Test the aws-marketplace report creation method no s3."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_marketplace_report(
            {"start_date": yesterday, "end_date": now, "aws_report_name": "cur_report", "write_monthly": True}
        )
        month_output_file_name = "{}-{}-{}-{}".format(
            calendar.month_name[now.month], now.year, "cur_report", "marketplace"
        )
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)

        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    @patch("nise.report.upload_to_s3")
    def test_aws_marketplace_create_report_with_s3(self, mock_upload_to_s3):
        """Test the aws-marketplace report creation method with s3."""
        mock_upload_to_s3.return_value = None
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": "my_bucket",
            "aws_report_name": "cur_report",
            "write_monthly": True,
        }
        aws_create_marketplace_report(options)
        month_output_file_name = "{}-{}-{}-{}".format(
            calendar.month_name[now.month], now.year, "cur_report", "marketplace"
        )
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)

        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    def test_aws_marketplace_create_report_with_local_dir(self):
        """Test the aws-marketplace report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "write_monthly": True,
        }
        aws_create_marketplace_report(options)
        month_output_file_name = "{}-{}-{}-{}".format(
            calendar.month_name[now.month], now.year, "cur_report", "marketplace"
        )
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)

        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_marketplace_create_report_with_local_dir_report_prefix(self):
        """Test the aws-marketplace report creation method with local directory and a report prefix."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "aws_bucket_name": local_bucket_path,
            "aws_report_name": "cur_report",
            "aws_prefix_name": "my_prefix",
            "write_monthly": True,
        }
        aws_create_marketplace_report(options)
        month_output_file_name = "{}-{}-{}-{}".format(
            calendar.month_name[now.month], now.year, "cur_report", "marketplace"
        )
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_marketplace_create_report_finalize_report_overwrite(self):
        """Test that an aws report file has an invoice id."""
        start_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.datetime.now().replace(day=5, hour=0, minute=0, second=0, microsecond=0)
        aws_create_marketplace_report(
            {
                "start_date": start_date,
                "end_date": end_date,
                "aws_report_name": "cur_report",
                "aws_finalize_report": "overwrite",
                "write_monthly": True,
            }
        )

        month_output_file_name = "{}-{}-{}".format(
            calendar.month_name[start_date.month], start_date.year, "cur_report"
        )
        expected_month_output_file = "{}/{}-{}.csv".format(os.getcwd(), month_output_file_name, "marketplace")
        self.assertTrue(os.path.isfile(expected_month_output_file))

        with open(expected_month_output_file, "r") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertNotEqual(row["bill/InvoiceId"], "")

        os.remove(expected_month_output_file)

    def test_aws_marketplace_create_report_without_write_monthly(self):
        """Test that monthly file is not created by default."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_marketplace_report({"start_date": yesterday, "end_date": now, "aws_report_name": "cur_report"})

        month_output_file_name = "{}-{}-{}-{}".format(
            calendar.month_name[now.month], now.year, "cur_report", "marketplace"
        )
        expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
        self.assertFalse(os.path.isfile(expected_month_output_file))


class OCPReportTestCase(TestCase):
    """
    TestCase class for OCP report functions.
    """

    def test_ocp_create_report(self):
        """Test the ocp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        cluster_id = "11112222"
        options = {"start_date": yesterday, "end_date": now, "ocp_cluster_id": cluster_id, "write_monthly": True}
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = "{}-{}-{}-{}".format(
                calendar.month_name[now.month], now.year, cluster_id, report_type
            )
            expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)

    def test_ocp_create_report_with_local_dir(self):
        """Test the ocp report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_insights_upload = mkdtemp()
        cluster_id = "11112222"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "insights_upload": local_insights_upload,
            "ocp_cluster_id": cluster_id,
            "write_monthly": True,
        }
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = "{}-{}-{}-{}".format(
                calendar.month_name[now.month], now.year, cluster_id, report_type
            )
            expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)
        shutil.rmtree(local_insights_upload)

    def test_ocp_create_report_with_local_dir_static_generation(self):
        """Test the ocp report creation method with local directory and static generation."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_insights_upload = mkdtemp()
        cluster_id = "11112222"
        static_ocp_data = {
            "generators": [
                {
                    "OCPGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "nodes": [
                            {
                                "node": None,
                                "node_name": "alpha",
                                "cpu_cores": 2,
                                "memory_gig": 4,
                                "namespaces": {
                                    "namespace_ci": {
                                        "pods": [
                                            {
                                                "pod": None,
                                                "pod_name": "pod_name1",
                                                "cpu_request": 5,
                                                "mem_request_gig": 2,
                                                "cpu_limit": 5,
                                                "mem_limit_gig": 2,
                                                "pod_seconds": 3600,
                                                "cpu_usage": {"1-21-2019": 1, "1-22-2019": 2, "1-23-2019": 4},
                                                "mem_usage_gig": {"1-21-2019": 1, "1-22-2019": 2, "1-23-2019": 4},
                                                "labels": "label_key1:label_value1|label_key2:label_value2",
                                            },
                                            {
                                                "pod": None,
                                                "pod_name": "pod_name2",
                                                "cpu_request": 10,
                                                "mem_request_gig": 4,
                                                "cpu_limit": 10,
                                                "mem_limit_gig": 4,
                                                "labels": "label_key3:label_value3|label_key4:label_value4",
                                            },
                                        ]
                                    }
                                },
                            }
                        ],
                    }
                }
            ]
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "insights_upload": local_insights_upload,
            "ocp_cluster_id": cluster_id,
            "static_report_data": static_ocp_data,
            "write_monthly": True,
        }
        ocp_create_report(options)

        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = "{}-{}-{}-{}".format(
                calendar.month_name[now.month], now.year, cluster_id, report_type
            )
            expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)
        shutil.rmtree(local_insights_upload)

    def test_ocp_create_report_with_local_dir_static_generation_with_dates(self):
        """Test the ocp report creation method with local directory and static generation with usage dates."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_insights_upload = mkdtemp()
        cluster_id = "11112222"
        static_ocp_data = {
            "generators": [
                {
                    "OCPGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "nodes": [
                            {
                                "node": None,
                                "node_name": "alpha",
                                "cpu_cores": 2,
                                "memory_gig": 4,
                                "start_date": str(now),
                                "end_date": str(now),
                                "namespaces": {
                                    "namespace_ci": {
                                        "pods": [
                                            {
                                                "pod": None,
                                                "pod_name": "pod_name1",
                                                "cpu_request": 5,
                                                "mem_request_gig": 2,
                                                "cpu_limit": 5,
                                                "mem_limit_gig": 2,
                                                "pod_seconds": 3600,
                                            },
                                            {
                                                "pod": None,
                                                "pod_name": "pod_name2",
                                                "cpu_request": 10,
                                                "mem_request_gig": 4,
                                                "cpu_limit": 10,
                                                "mem_limit_gig": 4,
                                            },
                                        ],
                                        "volumes": [
                                            {
                                                "volume": None,
                                                "volume_name": "pvc-1234",
                                                "storage_class": "gp2",
                                                "volume_request_gig": 20,
                                                "volume_claims": [
                                                    {
                                                        "volume_claim_name": "pod1_data",
                                                        "pod_name": "pod_name1",
                                                        "capacity_gig": 5,
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                },
                            }
                        ],
                    }
                }
            ]
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "insights_upload": local_insights_upload,
            "ocp_cluster_id": cluster_id,
            "static_report_data": static_ocp_data,
            "write_monthly": True,
        }
        ocp_create_report(options)

        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = "{}-{}-{}-{}".format(
                calendar.month_name[now.month], now.year, cluster_id, report_type
            )
            expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)

        shutil.rmtree(local_insights_upload)

    @patch.dict(os.environ, {"INSIGHTS_USER": "12345", "INSIGHTS_PASSWORD": "54321"})
    @patch("nise.report.requests.post")
    def test_ocp_route_file(self, mock_post):
        """Test that a response is good."""
        insights_user = os.environ.get("INSIGHTS_USER")
        insights_password = os.environ.get("INSIGHTS_PASSWORD")

        temp_file = NamedTemporaryFile(mode="w", delete=False)
        headers = ["col1", "col2"]
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_csv(temp_file.name, data, headers)

        insights_upload = "test"

        auth = (insights_user, insights_password)

        mock_post.return_value.status_code = 202
        ocp_route_file(insights_upload, temp_file.name)

        self.assertEqual(mock_post.call_args[1].get("auth"), auth)
        self.assertNotIn("headers", mock_post.call_args[1])

    def test_ocp_create_report_without_write_monthly(self):
        """Test that monthly file is not created by default."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        cluster_id = "11112222"
        options = {"start_date": yesterday, "end_date": now, "ocp_cluster_id": cluster_id}
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = "{}-{}-{}-{}".format(
                calendar.month_name[now.month], now.year, cluster_id, report_type
            )
            expected_month_output_file = "{}/{}.csv".format(os.getcwd(), month_output_file_name)
            self.assertFalse(os.path.isfile(expected_month_output_file))

    def test_ocp_create_report_with_local_dir_static_generation_multi_file(self):
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_insights_upload = mkdtemp()
        cluster_id = "11112222"
        static_ocp_data = {
            "generators": [
                {
                    "OCPGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "nodes": [
                            {
                                "node": None,
                                "node_name": "alpha",
                                "cpu_cores": 2,
                                "memory_gig": 4,
                                "start_date": str(yesterday.date()),
                                "end_date": str(now.date()),
                                "namespaces": {
                                    "namespace_ci": {
                                        "pods": [
                                            {
                                                "pod": None,
                                                "pod_name": "pod_name1",
                                                "cpu_request": 5,
                                                "mem_request_gig": 2,
                                                "cpu_limit": 5,
                                                "mem_limit_gig": 2,
                                                "pod_seconds": 3600,
                                            }
                                        ],
                                        "volumes": [
                                            {
                                                "volume": None,
                                                "volume_name": "pvc-1234",
                                                "storage_class": "gp2",
                                                "volume_request_gig": 20,
                                                "volume_claims": [
                                                    {
                                                        "volume_claim_name": "pod1_data",
                                                        "pod_name": "pod_name1",
                                                        "capacity_gig": 5,
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                },
                            }
                        ],
                    }
                }
            ]
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "insights_upload": local_insights_upload,
            "ocp_cluster_id": cluster_id,
            "static_report_data": static_ocp_data,
            "row_limit": 5,
            "write_monthly": True,
        }
        ocp_create_report(options)

        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            with self.subTest(report=report_type):
                month_output_file_name = "{}-{}-{}-{}".format(
                    calendar.month_name[now.month], now.year, cluster_id, report_type
                )
                month_output_file_pt_1 = f"{month_output_file_name}-1"
                month_output_file_pt_2 = f"{month_output_file_name}-2"

                expected_month_output_file_1 = "{}/{}.csv".format(os.getcwd(), month_output_file_pt_1)
                expected_month_output_file_2 = "{}/{}.csv".format(os.getcwd(), month_output_file_pt_2)

                print(f"{report_type}: {expected_month_output_file_1}")
                print(f"{report_type}: {expected_month_output_file_2}")

                self.assertTrue(os.path.isfile(expected_month_output_file_1))
                self.assertTrue(os.path.isfile(expected_month_output_file_2))

                # cleanup any leftover files
                regex = re.compile(month_output_file_name)
                for _, _, files in os.walk("."):
                    for fname in files:
                        if regex.match(fname):
                            os.remove(fname)

        shutil.rmtree(local_insights_upload)


class AzureReportTestCase(TestCase):
    """
    TestCase class for Azure report functions.
    """

    def setUp(self):
        """Setup shared variables for AzureReportTestCase."""
        self.MOCK_AZURE_REPORT_FILENAME = "{}/costreport_12345678-1234-5678-1234-567812345678.csv".format(os.getcwd())

    @staticmethod
    def mock_generate_azure_filename():
        """Create a fake azure filename."""
        fake_uuid = "12345678-1234-5678-1234-567812345678"
        output_file_name = "{}_{}".format("costreport", fake_uuid)
        local_path = "{}/{}.csv".format(os.getcwd(), output_file_name)
        output_file_name = output_file_name + ".csv"
        return local_path, output_file_name

    def test_generate_azure_filename(self):
        """Test that _generate_azure_filename returns not empty tuple."""
        tup = _generate_azure_filename()
        self.assertIsNotNone(tup[0])
        self.assertIsNotNone(tup[1])

    @patch("nise.report._generate_azure_filename")
    def test_azure_create_report(self, mock_name):
        """Test the azure report creation method."""
        mock_name.side_effect = self.mock_generate_azure_filename
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {"start_date": yesterday, "end_date": now, "write_monthly": True}
        azure_create_report(options)
        local_path = self.MOCK_AZURE_REPORT_FILENAME
        self.assertTrue(os.path.isfile(local_path))
        os.remove(local_path)

    @patch("nise.report._generate_azure_filename")
    def test_azure_create_report_with_static_data(self, mock_name):
        """Test the azure report creation method."""
        mock_name.side_effect = self.mock_generate_azure_filename
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        static_azure_data = {
            "generators": [
                {"BandwidthGenerator": {"start_date": str(yesterday.date()), "end_date": str(now.date())}},
                {
                    "SQLGenerator": {  # usage outside current month
                        "start_date": str(yesterday.date() + relativedelta(months=-2)),
                        "end_date": str(now.date() + relativedelta(months=-2)),
                    }
                },
                {
                    "StorageGenerator": {  # usage outside current month
                        "start_date": str(yesterday.date() + relativedelta(months=+2)),
                        "end_date": str(now.date() + relativedelta(months=+2)),
                    }
                },
            ]
        }
        options = {
            "start_date": yesterday,
            "end_date": now,
            "azure_prefix_name": "cost_report",
            "azure_report_name": "report",
            "azure_container_name": "cost",
            "static_report_data": static_azure_data,
            "write_monthly": True,
        }
        azure_create_report(options)
        local_path = self.MOCK_AZURE_REPORT_FILENAME
        self.assertTrue(os.path.isfile(local_path))
        os.remove(local_path)

    @patch("nise.report._generate_azure_filename")
    def test_azure_create_report_with_local_dir(self, mock_name):
        """Test the azure report creation method with local directory."""
        mock_name.side_effect = self.mock_generate_azure_filename
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_storage_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "azure_container_name": local_storage_path,
            "azure_report_name": "cur_report",
            "write_monthly": True,
        }
        azure_create_report(options)
        expected_month_output_file = self.MOCK_AZURE_REPORT_FILENAME
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_storage_path)

    @patch.dict(
        os.environ,
        {
            "AZURE_STORAGE_CONNECTION_STRING": (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={fake.word()};"
                f"AccountKey={fake.sha256()};"
                f"EndpointSuffix=core.windows.net"
            )
        },
    )
    @patch("nise.report.upload_to_azure_container")
    @patch("nise.report._generate_azure_filename")
    def test_azure_create_report_upload_to_azure(self, mock_name, mock_upload):
        """Test the azure upload is called when environment variable is set."""

        mock_name.side_effect = self.mock_generate_azure_filename
        mock_upload.return_value = True
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_storage_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "azure_account_name": fake.word(),
            "azure_prefic_name": "prefix",
            "azure_container_name": local_storage_path,
            "azure_report_name": "cur_report",
            "write_monthly": True,
        }
        azure_create_report(options)
        mock_upload.assert_called()
        os.remove(self.MOCK_AZURE_REPORT_FILENAME)

    @patch("nise.report._generate_azure_filename")
    def test_azure_create_report_without_write_monthly(self, mock_name):
        """Test that monthly file is not created by default."""
        mock_name.side_effect = self.mock_generate_azure_filename
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {"start_date": yesterday, "end_date": now}
        azure_create_report(options)
        local_path = self.MOCK_AZURE_REPORT_FILENAME
        self.assertFalse(os.path.isfile(local_path))


class GCPReportTestCase(TestCase):
    """
    Tests for GCP report generation.
    """

    def test_gcp_create_report(self):
        """Test the gcp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        gcp_create_report(
            {"start_date": yesterday, "end_date": now, "gcp_report_prefix": report_prefix, "write_monthly": True}
        )
        output_file_name = f"{report_prefix}.csv"
        expected_output_file_path = "{}/{}".format(os.getcwd(), output_file_name)

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_gcp_create_report_with_dataset_name(self):
        """Test the gcp report creation method where a dataset name is included."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        dataset_name = "test_name"
        gcp_create_report(
            {
                "start_date": yesterday,
                "end_date": now,
                "currency": "USD",
                "gcp_report_prefix": report_prefix,
                "write_monthly": True,
                "gcp_dataset_name": dataset_name,
            }
        )
        output_file_name = f"{report_prefix}.json"
        expected_output_file_path = "{}/{}".format(os.getcwd(), output_file_name)

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_gcp_create_report_with_dataset_name_no_report_prefix(self):
        """Test the gcp report creation method where a dataset name is included but no report prefix is included."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        dataset_name = "test_name"
        etag = "test_tag"
        gcp_create_report(
            {
                "start_date": yesterday,
                "end_date": now,
                "currency": "USD",
                "write_monthly": True,
                "gcp_dataset_name": dataset_name,
                "gcp_etag": etag,
            }
        )
        invoice_month = yesterday.strftime("%Y%m")
        scan_start = yesterday.date()
        scan_end = now.date()
        output_file_name = f"{invoice_month}_{etag}_{scan_start}:{scan_end}.json"
        expected_output_file_path = "{}/{}".format(os.getcwd(), output_file_name)
        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    @patch("nise.report.uuid4", side_effect=["nise"])
    def test_gcp_create_report_no_report_prefix(self, patch_etag):
        """Test the gcp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        gcp_create_report({"start_date": yesterday, "end_date": now, "write_monthly": True})
        invoice_month = yesterday.strftime("%Y%m")
        scan_start = yesterday.date()
        scan_end = now.date()
        expected_file_name = f"{invoice_month}_nise_{scan_start}:{scan_end}.csv"
        expected_output_file_path = "{}/{}".format(os.getcwd(), expected_file_name)
        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    @patch("nise.report.copy_to_local_dir")
    @patch("nise.report.upload_to_gcp_storage")
    def test_gcp_route_file_local(self, mock_upload, mock_copy):
        """Test that if bucket_name is a valid directory the file is not uploaded."""

        local_path = fake.file_path()
        remote_path = fake.file_path()

        with TemporaryDirectory() as temp_dir:
            gcp_route_file(temp_dir, local_path, remote_path)
            mock_copy.assert_called()
            mock_upload.assert_not_called()

    @patch("nise.report.copy_to_local_dir")
    @patch("nise.report.upload_to_gcp_storage")
    def test_gcp_route_file_upload(self, mock_upload, mock_copy):
        """Test that if bucket_name is not a valid directory the file is uploaded."""
        bucket = fake.file_path()
        local_path = fake.file_path()
        remote_path = fake.file_path()
        gcp_route_file(bucket, local_path, remote_path)

        mock_copy.assert_not_called()
        mock_upload.assert_called()

    def test_gcp_create_report_without_write_monthly(self):
        """Test that monthly file is not created by default."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        gcp_create_report({"start_date": yesterday, "end_date": now, "gcp_report_prefix": report_prefix})
        output_file_name = "{}-{}.csv".format(report_prefix, yesterday.strftime("%Y-%m-%d"))
        expected_output_file_path = "{}/{}".format(os.getcwd(), output_file_name)

        self.assertFalse(os.path.isfile(expected_output_file_path))

    def test_gcp_create_report_with_dataset_name_static_data(self):
        """Test the gcp report creation method where a dataset name is included and static data used."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        dataset_name = "test_name"
        cost = fake.pyint(min_value=10, max_value=1000)
        static_gcp_data = {
            "generators": [
                {
                    "ComputeEngineGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                    }
                },
                {
                    "CloudStorageGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                    }
                },
            ],
            "projects": [
                {
                    "billing_account_id": "example_account_id",
                    "project.name": "billion-force-58425800",
                    "project.id": "example-project-id",
                    "project.labels": "step:chair;year:each",
                    "location.location": "us-central1",
                    "location.country": "US",
                    "location.region": "us-central1",
                    "location.zone": "",
                }
            ],
        }
        gcp_create_report(
            {
                "start_date": yesterday,
                "end_date": now,
                "gcp_report_prefix": report_prefix,
                "write_monthly": True,
                "gcp_dataset_name": dataset_name,
                "static_report_data": static_gcp_data,
            }
        )
        output_file_name = f"{report_prefix}.json"
        expected_output_file_path = "{}/{}".format(os.getcwd(), output_file_name)

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_gcp_create_report_static_data(self):
        """Test the gcp report creation method where a dataset name is included and static data used."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        cost = fake.pyint(min_value=10, max_value=1000)
        static_gcp_data = {
            "generators": [
                {
                    "ComputeEngineGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                    }
                },
                {
                    "CloudStorageGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                    }
                },
            ],
            "projects": [
                {
                    "billing_account_id": "example_account_id",
                    "project.name": "billion-force-58425800",
                    "project.id": "example-project-id",
                    "project.labels": "step:chair;year:each",
                    "location.location": "us-central1",
                    "location.country": "US",
                    "location.region": "us-central1",
                    "location.zone": "",
                }
            ],
        }
        gcp_create_report(
            {
                "start_date": yesterday,
                "end_date": now,
                "gcp_report_prefix": report_prefix,
                "write_monthly": True,
                "static_report_data": static_gcp_data,
            }
        )
        output_file_name = f"{report_prefix}.csv"
        expected_output_file_path = "{}/{}".format(os.getcwd(), output_file_name)

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)


class OCIReportTestCase(TestCase):
    """Tests for OCI report generation."""

    @patch("nise.report._remove_files")
    def test_oci_create_report(self, mock_remove_files):
        """Test the oci create report method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        file_number = 0
        options = {"start_date": yesterday, "end_date": now, "write_monthly": False}
        oci_create_report(options)
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            file_name = f"reports_{report_type}-csv_0001{file_number}.csv"
            expected_output_file_path = f"{os.getcwd()}/{file_name}"
            self.assertTrue(os.path.isfile(expected_output_file_path))
            mock_remove_files.assert_called()
            os.remove(file_name)
            file_number += 1

    @patch("nise.report._write_csv")
    def test_write_oci_file(self, mock_write_csv):
        """Test that the write_oci_file method is called."""
        file_number = 0
        data = {"cost": [], "usage": []}
        options = {}
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            write_oci_file(report_type, file_number, data[report_type], options)
            assert mock_write_csv.called

    @patch("nise.report.copy_to_local_dir")
    def test_write_oci_file_to_local_bucket(self, mock_copy_to_local_dir):
        """Test the aws report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {
            "start_date": yesterday,
            "end_date": now,
            "oci_local_bucket": local_bucket_path,
            "write_monthly": True,
        }
        oci_create_report(options)
        assert mock_copy_to_local_dir.called
        cost_file_path = "{}/{}".format(os.getcwd(), "reports_cost-csv_00010.csv")
        usage_file_path = "{}/{}".format(os.getcwd(), "reports_usage-csv_00011.csv")
        self.assertTrue(os.path.isfile(cost_file_path))
        self.assertTrue(os.path.isfile(usage_file_path))
        os.remove(cost_file_path)
        os.remove(usage_file_path)
        shutil.rmtree(local_bucket_path)

    @patch("nise.report._write_csv")
    @patch("nise.report.upload_to_oci_bucket")
    def test_oci_bucket_upload(self, mock_write_csv, mock_oci_bucket_upload):
        """Test that the oci_bucket_upload method is called."""
        bucket_name = "test-bucket"
        file_number = 0
        data = {"cost": [], "usage": []}
        options = {"oci_bucket_name": bucket_name}
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            oci_bucket_upload(bucket_name, report_type, file_number, data[report_type], options)
            assert mock_write_csv.called
            assert mock_oci_bucket_upload.called

    @patch("nise.report.oci_bucket_upload")
    @patch("nise.report.write_oci_file")
    def test_oci_route_file_upload(self, mock_write_oci_file, mock_upload):
        """Test that file is uploaded if bucket_name is not none."""
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            bucket_name = "test-bucket"
            file_number = 0
            data = {"cost": [], "usage": []}
            options = {"oci_bucket_name": bucket_name}
            oci_route_file(report_type, file_number, data, options)
            mock_write_oci_file.assert_not_called()
            mock_upload.assert_called()

    @patch("nise.report.oci_bucket_upload")
    @patch("nise.report.write_oci_file")
    def test_oci_route_file_no_upload(self, mock_write_oci_file, mock_upload):
        """Test that file is not upload if bucket_name is none."""
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            file_number = 0
            data = {"cost": [], "usage": []}
            options = {"oci_bucket_name": None}
            oci_route_file(report_type, file_number, data, options)
            mock_write_oci_file.assert_called()
            mock_upload.assert_not_called()

    def test_oci_create_report_static_data(self):
        """Test oci report creation with static data."""

        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        cost = fake.pyint(min_value=10, max_value=1000)
        static_oci_data = {
            "generators": [
                {
                    "OCIComputeGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                        "currency": "USD",
                        "compartment_name": "testcompartmentname",
                        "tenant_id": "ocid1.tenancy.oc1..fjkEUoxyZSYLvd",
                    }
                },
                {
                    "OCIBlockStorageGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                        "currency": "USD",
                        "compartment_name": "testcompartmentname",
                        "tenant_id": "ocid1.tenancy.oc1..fjkEUoxyZSYLvd",
                    }
                },
                {
                    "OCINetworkGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                        "currency": "USD",
                        "compartment_name": "testcompartmentname",
                        "tenant_id": "ocid1.tenancy.oc1..fjkEUoxyZSYLvd",
                    }
                },
                {
                    "OCIDatabaseGenerator": {
                        "start_date": str(yesterday.date()),
                        "end_date": str(now.date()),
                        "cost": cost,
                        "currency": "USD",
                        "compartment_name": "testcompartmentname",
                        "tenant_id": "ocid1.tenancy.oc1..fjkEUoxyZSYLvd",
                    }
                },
            ],
        }
        oci_create_report(
            {
                "start_date": yesterday,
                "end_date": now,
                "write_monthly": True,
                "static_report_data": static_oci_data,
            }
        )
        cost_file_path = "{}/{}".format(os.getcwd(), "reports_cost-csv_00010.csv")
        usage_file_path = "{}/{}".format(os.getcwd(), "reports_usage-csv_00011.csv")

        self.assertTrue(os.path.isfile(cost_file_path))
        self.assertTrue(os.path.isfile(usage_file_path))
        os.remove(cost_file_path)
        os.remove(usage_file_path)
