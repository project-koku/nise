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
from unittest.mock import ANY
from unittest.mock import patch

import faker
from dateutil.relativedelta import relativedelta

from nise.__main__ import fix_dates
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
from nise.report import ocp_create_report
from nise.report import ocp_route_file
from nise.report import post_payload_to_ingest_service
from nise.report import write_gcp_file

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
        data = '[{"col1": "r1c1", "col2": "r1c2"},{"col1": "r2c1", "col2": "r2c2"}]'
        manifest_path = _write_manifest(data)
        self.assertTrue(os.path.exists(manifest_path))
        os.remove(manifest_path)

    def test_create_generator_for_dates_from_yaml(self):
        """Test helper function for generating dates."""
        month = {
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

    def test_create_generator_for_dates_from_yaml_within_month(self):
        month = {
            "start": datetime.datetime(2023, 5, 1, 0, 0),
            "end": datetime.datetime(2023, 5, 31, 23, 59),
        }

        attributes = {
            "start_date": datetime.datetime(2023, 5, 5, 0, 0),
            "end_date": datetime.datetime(2023, 5, 15, 15, 0),
        }

        start_date, end_date = _create_generator_dates_from_yaml(attributes, month)

        self.assertEqual(start_date, datetime.datetime(2023, 5, 5, 0, 0))
        self.assertEqual(end_date, datetime.datetime(2023, 5, 15, 15, 0))

    def test_create_generator_for_dates_from_yaml_within_month_before_month_start(self):
        month = {
            "start": datetime.datetime(2023, 5, 1, 0, 0),
            "end": datetime.datetime(2023, 5, 31, 23, 59),
        }

        attributes = {
            "start_date": datetime.datetime(2023, 4, 5, 0, 0),
            "end_date": datetime.datetime(2023, 5, 15, 15, 0),
        }

        start_date, end_date = _create_generator_dates_from_yaml(attributes, month)

        self.assertEqual(start_date, datetime.datetime(2023, 5, 1, 0, 0))
        self.assertEqual(end_date, datetime.datetime(2023, 5, 15, 15, 0))

    def test_create_generator_for_dates_from_yaml_within_month_ends_next_month(self):
        month = {
            "start": datetime.datetime(2023, 5, 1, 0, 0),
            "end": datetime.datetime(2023, 5, 31, 23, 59),
        }

        attributes = {
            "start_date": datetime.datetime(2023, 5, 5, 0, 0),
            "end_date": datetime.datetime(2023, 8, 15, 15, 0),
        }

        start_date, end_date = _create_generator_dates_from_yaml(attributes, month)

        self.assertEqual(start_date, datetime.datetime(2023, 5, 5, 0, 0))
        self.assertEqual(end_date, datetime.datetime(2023, 5, 31, 23, 59))

    def test_create_generator_for_dates_from_yaml_first_month(self):
        """Test that correct dates are generated on the first of the month"""
        previous_month = {
            "start": datetime.datetime(2024, 2, 1, 0, 0, tzinfo=datetime.UTC),
            "end": datetime.datetime(2024, 3, 1, 0, 0, tzinfo=datetime.UTC),
        }
        current_month = {
            "start": datetime.datetime(2024, 3, 1, 0, 0, tzinfo=datetime.UTC),
            "end": datetime.datetime(2024, 4, 1, 0, 0, tzinfo=datetime.UTC),
        }

        attributes = {
            "start_date": datetime.datetime(2024, 2, 1, 0, 0, tzinfo=datetime.UTC),
            "end_date": datetime.datetime(2024, 3, 1, 23, 0, tzinfo=datetime.UTC),
        }

        start_date_previous, end_date_previous = _create_generator_dates_from_yaml(attributes, previous_month)

        self.assertEqual(start_date_previous, datetime.datetime(2024, 2, 1, 0, 0, tzinfo=datetime.UTC))
        self.assertEqual(end_date_previous, datetime.datetime(2024, 3, 1, 0, 0, tzinfo=datetime.UTC))

        start_date_current, end_date_current = _create_generator_dates_from_yaml(attributes, current_month)

        self.assertEqual(start_date_current, datetime.datetime(2024, 3, 1, 0, 0, tzinfo=datetime.UTC))
        self.assertEqual(end_date_current, datetime.datetime(2024, 3, 1, 23, 0, tzinfo=datetime.UTC))

    def test_create_generator_for_dates_from_yaml_middle_month(self):
        """Test helper function for generating dates verifying the middle month in a 3 month range."""
        month = {
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
        self.maxDiff = None
        test_matrix = [
            {
                "start_date": datetime.datetime(year=2018, month=1, day=15),
                "end_date": datetime.datetime(year=2018, month=1, day=30, hour=23, minute=59),
                "expected_list": [
                    {
                        "name": "January",
                        "start": datetime.datetime(year=2018, month=1, day=15, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2018, month=1, day=30, hour=23, minute=59, tzinfo=datetime.UTC),
                    }
                ],
            },
            {
                "start_date": datetime.datetime(year=2018, month=11, day=15),
                "end_date": datetime.datetime(year=2019, month=1, day=5, hour=23, minute=59),
                "expected_list": [
                    {
                        "name": "November",
                        "start": datetime.datetime(year=2018, month=11, day=15, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2018, month=12, day=1, hour=0, minute=0, tzinfo=datetime.UTC),
                    },
                    {
                        "name": "December",
                        "start": datetime.datetime(year=2018, month=12, day=1, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2019, month=1, day=1, hour=0, minute=0, tzinfo=datetime.UTC),
                    },
                    {
                        "name": "January",
                        "start": datetime.datetime(year=2019, month=1, day=1, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2019, month=1, day=5, hour=23, minute=59, tzinfo=datetime.UTC),
                    },
                ],
            },
            {
                "start_date": datetime.datetime(year=2021, month=6, day=1),
                "end_date": datetime.datetime(year=2021, month=7, day=29),
                "expected_list": [
                    {
                        "name": "June",
                        "start": datetime.datetime(year=2021, month=6, day=1, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2021, month=7, day=1, hour=0, minute=0, tzinfo=datetime.UTC),
                    },
                    {
                        "name": "July",
                        "start": datetime.datetime(year=2021, month=7, day=1, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2021, month=7, day=29, hour=0, minute=0, tzinfo=datetime.UTC),
                    },
                ],
            },
            {
                # FIXME
                #
                # When the start_date hour=0, this fails because there is an extra entry in the output.
                #
                # Output when start_date hour=0 on a month boundary:
                #    [
                #        {
                #            'name': 'July',
                #            'start': datetime.datetime(2023, 7, 31, 0, 0, tzinfo=datetime.timezone.utc),
                #            'end': datetime.datetime(2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc)
                #        },
                #        {
                #            'name': 'August',
                #            'start': datetime.datetime(2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc),
                #            'end': datetime.datetime(2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc)
                #        },
                #    ]
                #
                "start_date": datetime.datetime(year=2023, month=7, day=31, hour=1),  # Failure when hour=0
                "end_date": datetime.datetime(year=2023, month=8, day=1),
                "expected_list": [
                    {
                        "name": "July",
                        "start": datetime.datetime(year=2023, month=7, day=31, hour=1, minute=0, tzinfo=datetime.UTC),
                        "end": datetime.datetime(year=2023, month=8, day=1, hour=0, minute=0, tzinfo=datetime.UTC),
                    },
                    # {
                    #     "name": "August",
                    #     "start": datetime.datetime(
                    #         year=2023, month=8, day=1, hour=0, minute=0, tzinfo=datetime.timezone.utc
                    #     ),
                    #     "end": datetime.datetime(
                    #         year=2023, month=8, day=1, hour=0, minute=0, tzinfo=datetime.timezone.utc
                    #     )
                    # },
                ],
            },
        ]

        for test_case in test_matrix:
            with self.subTest(test=test_case):
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
        """Test that the basic auth path is taken."""
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

    @patch.dict(os.environ, {"HCC_SERVICE_ACCOUNT_ID": "12345", "HCC_SERVICE_ACCOUNT_SECRET": "54321"})
    @patch("nise.report.requests.post")
    def test_post_payload_to_ingest_service_with_service_account(self, mock_post):
        """Test that the service account path is taken."""
        temp_file = NamedTemporaryFile(mode="w", delete=False)
        headers = ["col1", "col2"]
        data = [{"col1": "r1c1", "col2": "r1c2"}, {"col1": "r2c1", "col2": "r2c2"}]
        _write_csv(temp_file.name, data, headers)

        insights_upload = {}
        data = {}

        post_payload_to_ingest_service(insights_upload, temp_file.name)
        self.assertEqual(mock_post.call_args[1].get("data"), data)

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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        fix_dates(options, "aws")
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        fix_dates(options, "aws")
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        fix_dates(options, "aws")
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[start_date.month], start_date.year, "cur_report")
        finalized_file_name = f"{month_output_file_name}-finalized"
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
        expected_finalized_file = f"{os.getcwd()}/{finalized_file_name}.csv"
        self.assertTrue(os.path.isfile(expected_month_output_file))
        self.assertTrue(os.path.isfile(expected_finalized_file))
        with open(expected_month_output_file) as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertEqual(row["bill/InvoiceId"], "")

        with open(expected_finalized_file) as f:
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

        month_output_file_name = "{}-{}-{}".format(calendar.month_name[start_date.month], start_date.year, "cur_report")
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
        self.assertTrue(os.path.isfile(expected_month_output_file))

        with open(expected_month_output_file) as f:
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
        fix_dates(options, "aws")
        aws_create_report(options)
        month_output_file_name = "{}-{}-{}".format(calendar.month_name[now.month], now.year, "cur_report")
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
            "generators": [{"EC2Generator": {"start_date": str(yesterday), "end_date": str(now)}}],
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
        fix_dates(options, "aws")
        aws_create_report(options)
        month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-cur_report"
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        fix_dates(options, "aws")
        aws_create_report(options)
        month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-cur_report"
        expected_month_output_file_1 = f"{os.path.join(os.getcwd(), month_output_file_name)}-1"
        expected_month_output_file_2 = f"{os.path.join(os.getcwd(), month_output_file_name)}-2"

        if now.day == 1:
            # First of the month will have numbered files for the previous month but not the current month
            expected_month_output_file_1 = f"{os.path.join(os.getcwd(), month_output_file_name)}"
            expected_month_output_file_2 = os.path.join(
                os.getcwd(), f"{calendar.month_name[yesterday.month]}-{yesterday.year}-cur_report-1"
            )

        self.assertTrue(os.path.isfile(f"{expected_month_output_file_1}.csv"))
        self.assertTrue(os.path.isfile(f"{expected_month_output_file_2}.csv"))

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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"

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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"

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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"

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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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

        month_output_file_name = "{}-{}-{}".format(calendar.month_name[start_date.month], start_date.year, "cur_report")
        expected_month_output_file = "{}/{}-{}.csv".format(os.getcwd(), month_output_file_name, "marketplace")
        self.assertTrue(os.path.isfile(expected_month_output_file))

        with open(expected_month_output_file) as f:
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
        expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        options = {
            "start_date": yesterday,
            "end_date": now,
            "ocp_cluster_id": cluster_id,
            "write_monthly": True,
            "ros_ocp_info": True,
        }
        fix_dates(options, "ocp")
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)

    def test_ocp_create_report_ros_ocp_constant_data_generation(self):
        """Test the ocp report creation method with constant_values_ros_ocp enabled."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        cluster_id = "11112222"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "ocp_cluster_id": cluster_id,
            "write_monthly": True,
            "ros_ocp_info": True,
            "constant_values_ros_ocp": True,
        }
        fix_dates(options, "ocp")
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)

    def test_ocp_create_report_minio_upload(self):
        """Test the ocp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        cluster_id = "11112222"
        mock_minio_url = "fake-minio-url"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "ocp_cluster_id": cluster_id,
            "write_monthly": True,
            "ros_ocp_info": True,
            "minio_upload": mock_minio_url,
        }
        fix_dates(options, "ocp")
        with patch("nise.report.post_payload_to_minio") as mock_upload:
            mock_upload.return_value.status_code = 200
            ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
            self.assertTrue(os.path.isfile(expected_month_output_file))
            os.remove(expected_month_output_file)
        mock_upload.assert_called()
        mock_upload.assert_called_with(mock_minio_url, ANY, ANY)

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
            "ros_ocp_info": True,
        }
        fix_dates(options, "ocp")
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        fix_dates(options, "ocp")
        ocp_create_report(options)

        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            if "ocp_ros_usage" == report_type:
                continue
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        fix_dates(options, "ocp")
        ocp_create_report(options)

        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            if "ocp_ros_usage" == report_type:
                continue
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
        options = {"start_date": yesterday, "end_date": now, "ocp_cluster_id": cluster_id, "ros_ocp_info": True}
        fix_dates(options, "ocp")
        ocp_create_report(options)
        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
            expected_month_output_file = f"{os.getcwd()}/{month_output_file_name}.csv"
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
                                        "virtual_machines": [{"virtual_machine": "test-machine"}],
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
        fix_dates(options, "ocp")
        ocp_create_report(options)

        for report_type in OCP_REPORT_TYPE_TO_COLS.keys():
            if "ocp_ros_usage" == report_type:
                continue
            with self.subTest(report=report_type):
                month_output_file_name = f"{calendar.month_name[now.month]}-{now.year}-{cluster_id}-{report_type}"
                month_output_file_pt_1 = f"{month_output_file_name}-1"
                month_output_file_pt_2 = f"{month_output_file_name}-2"

                if now.day == 1:
                    # First of the month will have numbered files for the previous month but not the current month
                    month_output_file_pt_1 = month_output_file_name
                    month_output_file_pt_2 = (
                        f"{calendar.month_name[yesterday.month]}-{yesterday.year}-{cluster_id}-{report_type}-1"
                    )

                expected_month_output_file_1 = os.path.join(os.getcwd(), month_output_file_pt_1)
                expected_month_output_file_2 = os.path.join(os.getcwd(), month_output_file_pt_2)

                print(f"{report_type}: {expected_month_output_file_1}")
                print(f"{report_type}: {expected_month_output_file_2}")
                self.assertTrue(os.path.isfile(f"{expected_month_output_file_1}.csv"))
                self.assertTrue(os.path.isfile(f"{expected_month_output_file_2}.csv"))

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
        self.MOCK_AZURE_REPORT_FILENAME = os.path.join(
            os.getcwd(), "costreport_12345678-1234-5678-1234-567812345678_0001.csv"
        )

    @staticmethod
    def mock_generate_azure_filename(file_number):
        """Create a fake azure filename with file number."""
        fake_uuid = "12345678-1234-5678-1234-567812345678"
        suffix = f"{file_number:04d}"
        output_file_name = f"costreport_{fake_uuid}_{suffix}.csv"
        local_path = os.path.join(os.getcwd(), output_file_name)
        return local_path, output_file_name

    def test_generate_azure_filename(self):
        """Test that _generate_azure_filename returns not empty tuple."""
        tup = _generate_azure_filename(1)
        self.assertIsNotNone(tup[0])
        self.assertIsNotNone(tup[1])
        self.assertTrue(tup[1].endswith("_0001.csv"))

    @patch("nise.report._generate_azure_filename")
    def test_azure_create_report(self, mock_name):
        """Test the azure report creation method."""
        mock_name.side_effect = self.mock_generate_azure_filename
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {"start_date": yesterday, "end_date": now, "write_monthly": True}
        fix_dates(options, "azure")
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
            ],
            "accounts": {
                "payer": "38f1d748-3ac7-4b7f-a5ae-8b5ff16db82c",
                "user": ["38f1d748-3ac7-4b7f-a5ae-8b5ff16db82c"],
                "subscription_name": "static_subscription_name",
            },
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
        fix_dates(options, "azure")
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
        fix_dates(options, "azure")
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
        fix_dates(options, "azure")
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
        fix_dates(options, "azure")
        azure_create_report(options)
        local_path = self.MOCK_AZURE_REPORT_FILENAME
        self.assertFalse(os.path.isfile(local_path))

    def test_azure_report_file_row_limit(self):
        """Test Azure report splits files based on file_row_limit."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day

        options = {"start_date": yesterday, "end_date": now, "write_monthly": True, "row_limit": 10}

        fix_dates(options, "azure")
        azure_create_report(options)

        files = [f for f in os.listdir(os.getcwd()) if re.match(r"^[\w-]+_\d{4}\.csv$", f)]
        self.assertGreater(len(files), 1)

        for f in files:
            os.remove(f)


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
        options = {"start_date": yesterday, "end_date": now, "gcp_report_prefix": report_prefix, "write_monthly": True}
        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = f"{report_prefix}_0001.csv"
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_gcp_create_report_resource_level(self):
        """Test the gcp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "gcp_report_prefix": report_prefix,
            "write_monthly": True,
            "gcp_dataset_name": "gcp-resource-dataset",
            "gcp_resource_level": True,
        }
        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = f"{report_prefix}.json"
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_gcp_create_report_with_dataset_name(self):
        """Test the gcp report creation method where a dataset name is included."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_report"
        dataset_name = "test_name"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "currency": "USD",
            "gcp_report_prefix": report_prefix,
            "write_monthly": True,
            "gcp_dataset_name": dataset_name,
        }

        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = f"{report_prefix}.json"
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_gcp_create_report_with_dataset_name_no_report_prefix(self):
        """Test the gcp report creation method where a dataset name is included but no report prefix is included."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        dataset_name = "test_name"
        etag = "test_tag"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "currency": "USD",
            "write_monthly": True,
            "gcp_dataset_name": dataset_name,
            "gcp_etag": etag,
        }

        fix_dates(options, "gcp")
        gcp_create_report(options)
        invoice_month = yesterday.strftime("%Y%m")
        scan_start = yesterday.date()
        scan_end = now.date()
        output_file_name = f"{invoice_month}_{etag}_{scan_start}:{scan_end}.json"
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"
        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    @patch("nise.report.uuid4", return_value="25150e4f-bfe5-406b-aaa9-b19f59875420")
    def test_gcp_create_report_no_report_prefix(self, patch_etag):
        """Test the gcp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {"start_date": yesterday, "end_date": now, "write_monthly": True}
        fix_dates(options, "gcp")
        gcp_create_report(options)
        invoice_month = yesterday.strftime("%Y%m")
        scan_start = yesterday.date()
        scan_end = now.date()
        expected_file_name = f"{invoice_month}_{patch_etag.return_value}_{scan_start}:{scan_end}_0001.csv"
        expected_output_file_path = f"{os.getcwd()}/{expected_file_name}"
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
        options = {"start_date": yesterday, "end_date": now, "gcp_report_prefix": report_prefix}
        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = "{}-{}.csv".format(report_prefix, yesterday.strftime("%Y-%m-%d"))
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}_0001.csv"
        self.assertFalse(os.path.isfile(expected_output_file_path))

    def test_gcp_create_report_without_write_monthly_overlapping_month(self):
        """Test that there are no Exceptions when processing overlapping months dates."""
        now = datetime.datetime(2024, 7, 1, 0, 0)
        yesterday = datetime.datetime(2024, 6, 30, 0, 0)
        report_prefix = "test_report"
        options = {
            "start_date": yesterday,
            "end_date": now,
            "gcp_report_prefix": report_prefix,
            "gcp_bucket_name": "gcp_bucket_name",
        }
        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = "{}-{}.csv".format(report_prefix, yesterday.strftime("%Y-%m-%d"))
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

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

        options = {
            "start_date": yesterday,
            "end_date": now,
            "gcp_report_prefix": report_prefix,
            "write_monthly": True,
            "gcp_dataset_name": dataset_name,
            "static_report_data": static_gcp_data,
        }
        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = f"{report_prefix}.json"
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

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
        options = {
            "start_date": yesterday,
            "end_date": now,
            "gcp_report_prefix": report_prefix,
            "write_monthly": True,
            "static_report_data": static_gcp_data,
        }
        fix_dates(options, "gcp")
        gcp_create_report(options)
        output_file_name = f"{report_prefix}_0001.csv"
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

        self.assertTrue(os.path.isfile(expected_output_file_path))
        os.remove(expected_output_file_path)

    def test_write_gcp_file_with_resource_data(self):
        """Test that resource data is created."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        report_prefix = "test_resource_report"
        data = [{"resource.name": "Baked", "resource.global_name": "Beans"}]
        write_gcp_file(yesterday, now, data, {"gcp_report_prefix": report_prefix, "gcp_resource_level": True}, 1)
        output_file_name = "{}-{}.csv".format(report_prefix, yesterday.strftime("%Y-%m-%d"))
        expected_output_file_path = f"{os.getcwd()}/{output_file_name}"

        self.assertFalse(os.path.isfile(expected_output_file_path))

    def test_gcp_report_file_row_limit(self):
        """Test GCP report splits files based on file_row_limit."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day

        options = {
            "start_date": yesterday,
            "end_date": now,
            "gcp_report_prefix": "test_report_gcp",
            "write_monthly": True,
            "row_limit": 10,
        }

        fix_dates(options, "gcp")
        gcp_create_report(options)

        files = [f for f in os.listdir(os.getcwd()) if re.match(r"^[\w-]+_\d{4}\.csv$", f)]
        self.assertGreater(len(files), 1)

        for f in files:
            os.remove(f)
