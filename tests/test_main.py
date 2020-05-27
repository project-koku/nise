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
import argparse
import builtins
import os
from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

from nise.__main__ import _load_static_report_data
from nise.__main__ import _load_yaml_file
from nise.__main__ import _validate_provider_inputs
from nise.__main__ import create_parser
from nise.__main__ import main
from nise.__main__ import valid_date


class MockGen:
    def init_config(self, *args, **kwargs):
        return

    def process_template(self, *args, **kwargs):
        return


class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """

    @classmethod
    def setUpClass(cls):
        parser = create_parser()
        cls.parser = parser

    def test_valid_date(self):
        """Test valid date."""
        date_obj = date(2018, 1, 2)
        date_str = "2018-01-02"
        out_date = valid_date(date_str)
        self.assertEqual(date_obj, out_date.date())

    @patch("nise.__main__.argparse.ArgumentParser.parse_args")
    def test_with_empty_args(self, mock_args):
        """
        User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            mock_args.return_value = argparse.Namespace(command=None)
            main()

    def test_main_with_report_args(self):
        """
        Test main returns None with valid args.
        """
        args = ["report", "aws", "--start-date", str(date.today())]
        parsed_args = self.parser.parse_args(args)
        options = vars(parsed_args)
        with patch("nise.__main__.run"):
            with patch.object(builtins, "vars") as mock_options:
                with patch("nise.__main__.argparse.ArgumentParser.parse_args") as mock_args:
                    mock_args.return_value = parsed_args
                    mock_options.return_value = options
                    self.assertIsNone(main())

    def test_invalid_start(self):
        """
        Test where user passes an invalid date format.
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["report", "ocp", "--start-date", "foo"])

    def test_valid_s3_no_input(self):
        """
        Test where user passes no s3 argument combination.
        """
        args = ["report", "aws", "--start-date", str(date.today())]
        options = vars(self.parser.parse_args(args))
        self.assertTrue(_validate_provider_inputs(self.parser, options))

    def test_valid_s3_both_inputs(self):
        """
        Test where user passes a valid s3 argument combination.
        """
        args = [
            "report",
            "aws",
            "--start-date",
            str(date.today()),
            "--aws-s3-bucket-name",
            "mybucket",
            "--aws-s3-report-name",
            "cur",
        ]
        options = vars(self.parser.parse_args(args))
        self.assertTrue(_validate_provider_inputs(self.parser, options))

    def test_valid_azure_no_input(self):
        """
        Test where user passes no s3 argument combination.
        """
        args = ["report", "azure", "--start-date", str(date.today())]
        options = vars(self.parser.parse_args(args))
        self.assertTrue(_validate_provider_inputs(self.parser, options))

    def test_valid_azure_inputs(self):
        """
        Test where user passes a valid s3 argument combination.
        """
        args = [
            "report",
            "azure",
            "--start-date",
            str(date.today()),
            "--azure-container-name",
            "storage",
            "--azure-report-name",
            "report",
            "--azure-report-prefix",
            "value",
            "--azure-account-name",
            "account",
        ]
        options = vars(self.parser.parse_args(args))
        valid = _validate_provider_inputs(self.parser, options)
        self.assertTrue(valid)

    def test_invalid_s3_inputs(self):
        """
        Test where user passes an invalid s3 argument combination.
        """
        with self.assertRaises(SystemExit):
            args = ["report", "aws", "--start-date", str(date.today()), "--aws-s3-bucket-name", "mybucket"]
            options = vars(self.parser.parse_args(args))
            _validate_provider_inputs(self.parser, options)

    def test_invalid_aws_inputs(self):
        """
        Test where user passes an invalid aws argument combination.
        """
        with self.assertRaises(SystemExit):
            args = ["report", "aws", "--start-date", str(date.today()), "--ocp-cluster-id", "123"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "aws", "--start-date", str(date.today()), "--azure-container-name", "123"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "aws", "--start-date", str(date.today()), "--gcp-report-prefix", "gcp-report"]
            self.parser.parse_args(args)

    def test_invalid_azure_inputs(self):
        """
        Test where user passes an invalid azure argument combination.
        """
        with self.assertRaises(SystemExit):
            args = ["report", "azure", "--start-date", str(date.today()), "--azure-report-name", "report"]
            options = vars(self.parser.parse_args(args))
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            args = ["report", "azure", "--start-date", str(date.today()), "--aws-s3-bucket-name", "mybucket"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "azure", "--start-date", str(date.today()), "--ocp-cluster-id", "123"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "azure", "--start-date", str(date.today()), "--gcp-report-prefix", "gcp-report"]
            self.parser.parse_args(args)

    def test_invalid_ocp_inputs(self):
        """
        Test where user passes an invalid ocp argument combination.
        """
        with self.assertRaises(SystemExit):
            args = ["report", "ocp", "--start-date", str(date.today()), "--aws-s3-bucket-name", "mybucket"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "ocp", "--start-date", str(date.today()), "--azure-report-name", "report"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "ocp", "--start-date", str(date.today()), "--gcp-report-prefix", "gcp-report"]
            self.parser.parse_args(args)

    @patch.dict(os.environ, {"INSIGHTS_ACCOUNT_ID": "12345", "INSIGHTS_ORG_ID": "54321"})
    def test_ocp_inputs_insights_upload_account_org_ids(self):
        """
        Test where user passes an invalid ocp argument combination.
        """

        args = [
            "report",
            "ocp",
            "--start-date",
            str(date.today()),
            "--insights-upload",
            "true",
            "--ocp-cluster-id",
            "123",
        ]
        options = vars(self.parser.parse_args(args))
        is_valid, _ = _validate_provider_inputs(self.parser, options)
        self.assertTrue(is_valid)

    @patch.dict(os.environ, {"INSIGHTS_USER": "12345", "INSIGHTS_PASSWORD": "54321"})
    def test_ocp_inputs_insights_upload_user_pass(self):
        """
        Test where user passes an invalid ocp argument combination.
        """

        args = [
            "report",
            "ocp",
            "--start-date",
            str(date.today()),
            "--insights-upload",
            "true",
            "--ocp-cluster-id",
            "123",
        ]
        options = vars(self.parser.parse_args(args))
        is_valid, _ = _validate_provider_inputs(self.parser, options)
        self.assertTrue(is_valid)

    def test_ocp_inputs_insights_upload_no_envs(self):
        """
        Test where user passes an invalid ocp argument combination.
        """
        with self.assertRaises(SystemExit):
            args = [
                "report",
                "ocp",
                "--start-date",
                str(date.today()),
                "--insights-upload",
                "true",
                "--ocp-cluster-id",
                "123",
            ]
            options = vars(self.parser.parse_args(args))
            _validate_provider_inputs(self.parser, options)

    def test_ocp_no_cluster_id(self):
        """
        Test where user passes ocp without cluster id combination.
        """
        with self.assertRaises(SystemExit):
            args = ["report", "ocp", "--start-date", str(date.today())]
            options = vars(self.parser.parse_args(args))
            _validate_provider_inputs(self.parser, options)

    def test_ocp_no_insights_upload(self):
        """
        Test where user passes ocp without insights upload.
        """
        args = ["report", "ocp", "--start-date", str(date.today()), "--ocp-cluster-id", "132"]
        options = vars(self.parser.parse_args(args))
        is_valid, _ = _validate_provider_inputs(self.parser, options)
        self.assertTrue(is_valid)

    def test_main_no_inputs(self):
        """
        Test execution of main without inputs.
        """
        with self.assertRaises(SystemExit):
            main()

    def test_load_yaml_file(self):
        """
        Test to load static report yaml file.
        """
        data = _load_yaml_file("tests/aws_static_report.yml")
        self.assertIsNotNone(data)

        data_missing = _load_yaml_file(None)
        self.assertIsNone(data_missing)

    def test_load_static_report_data(self):
        """
        Test to load static report data from option.
        """
        options = {"start_date": date.today(), "static_report_file": "tests/aws_static_report.yml"}

        _load_static_report_data(options)
        self.assertIsNotNone(options["static_report_data"])
        self.assertIsNotNone(options["start_date"])
        self.assertIsNotNone(options["end_date"])

        missing_options = {}
        _load_static_report_data(missing_options)
        self.assertIsNone(missing_options.get("static_report_data"))

    def test_load_static_report_data_no_start_date(self):
        """
        Test to load static report data from option with no start date.
        """
        options = {"static_report_file": "tests/aws_static_report.yml"}
        _load_static_report_data(options)
        self.assertIsNotNone(options.get("start_date"))
        self.assertIsNotNone(options.get("end_date"))

    def test_load_static_report_data_azure_dates(self):
        """Test correct dates for Azure.

        Azure is different than AWS/OCP. End date needs to be the next day.
        """
        args = [
            "report",
            "azure",
            "--static-report-file",
            "tests/azure_static_report.yml",
            "--azure-container-name",
            "storage",
            "--azure-report-name",
            "report",
        ]
        options = vars(self.parser.parse_args(args))
        _load_static_report_data(options)
        gen_values = dict(*options.get("static_report_data").get("generators")[0].values())
        self.assertEqual(
            gen_values.get("start_date"), str(datetime.now().replace(microsecond=0, second=0, minute=0, hour=0))
        )
        self.assertEqual(
            gen_values.get("end_date"),
            str(datetime.now().replace(microsecond=0, second=0, minute=0) + timedelta(hours=24)),
        )

    def test_invalid_gcp_inputs(self):
        """
        Test where user args from azure, ocp, and aws when creating gcp data.
        """
        with self.assertRaises(SystemExit):
            args = ["report", "gcp", "--start-date", str(date.today()), "--azure-account-name", "account"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "gcp", "--start-date", str(date.today()), "--aws-s3-bucket-name", "mybucket"]
            self.parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ["report", "gcp", "--start-date", str(date.today()), "--ocp-cluster-id", "123"]
            self.parser.parse_args(args)

    def test_no_provider_type_fail(self):
        """
        Test that parser fails when no provider type is passed.
        """
        with self.assertRaises(SystemExit):
            options = {}
            _validate_provider_inputs(self.parser, options)

    def test_yml_valid(self):
        """Test the yaml parser."""
        args = ["yaml", "ocp", "-o", "large.yml"]
        self.parser.parse_args(args)

    def test_yml_invalid(self):
        """Test the yaml parser."""
        arg_options = [["ocp"], ["ocp", "-o"]]
        for option in arg_options:
            with self.subTest(additional_options=option), self.assertRaises(SystemExit):
                args = ["yaml"] + option
                self.parser.parse_args(args)

    def test_main_with_yaml_args(self):
        """Test main returns None with valid args."""
        args = ["yaml", "aws", "-o", "large.yml"]
        parsed_args = self.parser.parse_args(args)
        options = vars(parsed_args)
        with patch("nise.yaml_gen.GENERATOR_MAP") as mock_get:
            mock_get.return_value = MockGen()
            with patch.object(builtins, "vars") as mock_options:
                with patch("nise.__main__.argparse.ArgumentParser.parse_args") as mock_args:
                    mock_args.return_value = parsed_args
                    mock_options.return_value = options
                    self.assertIsNone(main())
