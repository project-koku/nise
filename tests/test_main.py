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
from datetime import datetime, date
from unittest import TestCase
from unittest.mock import patch

from nise.__main__ import (create_parser,
                           main,
                           _load_yaml_file,
                           _load_static_report_data,
                           _validate_provider_inputs,
                           valid_date)


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
        date_str = '2018-01-02'
        out_date = valid_date(date_str)
        self.assertEqual(date_obj, out_date.date())

    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])
        with self.assertRaises(SystemExit):
            options = {'aws': False, 'ocp': False, 'azure': False}
            _validate_provider_inputs(self.parser, options)

    def test_invalid_start(self):
        """
        Test where user passes an invalid date format.
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['--start-date', 'foo'])

    def test_valid_s3_no_input(self):
        """
        Test where user passes no s3 argument combination.
        """
        options = {'aws': True}
        valid = _validate_provider_inputs(self.parser, options)
        self.assertTrue(valid)

    def test_valid_s3_both_inputs(self):
        """
        Test where user passes a valid s3 argument combination.
        """
        options = {'aws': True,
                   'aws_bucket_name': 'mybucket',
                   'aws_report_name': 'cur'}
        valid = _validate_provider_inputs(self.parser, options)
        self.assertTrue(valid)

    def test_valid_azure_no_input(self):
        """
        Test where user passes no s3 argument combination.
        """
        options = {'azure': True}
        valid = _validate_provider_inputs(self.parser, options)
        self.assertTrue(valid)

    def test_valid_azure_inputs(self):
        """
        Test where user passes a valid s3 argument combination.
        """
        options = {'azure': True,
                   'azure_container_name': 'storage',
                   'azure_report_name': 'report',
                   'azure_prefix_name': 'value'}
        valid = _validate_provider_inputs(self.parser, options)
        self.assertTrue(valid)

    def test_invalid_s3_inputs(self):
        """
        Test where user passes an invalid s3 argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'aws': True, 'aws_bucket_name': 'mybucket'}
            _validate_provider_inputs(self.parser, options)

    def test_invalid_aws_inputs(self):
        """
        Test where user passes an invalid aws argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'aws': True, 'ocp_cluster_id': '123'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'aws': True, 'azure_container_name': '123'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'azure': True, 'gcp_report_prefix': 'gcp-report'}
            _validate_provider_inputs(self.parser, options)

    def test_invalid_azure_inputs(self):
        """
        Test where user passes an invalid azure argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'azure': True, 'azure_report_name': 'report'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'azure': True, 'aws_bucket_name': 'mybucket'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'azure': True, 'ocp_cluster_id': '123'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'azure': True, 'gcp_report_prefix': 'gcp-report'}
            _validate_provider_inputs(self.parser, options)

    def test_invalid_ocp_inputs(self):
        """
        Test where user passes an invalid ocp argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'ocp': True, 'aws_bucket_name': 'mybucket'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'ocp': True, 'azure_container_name': '123'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'azure': True, 'gcp_report_prefix': 'gcp-report'}
            _validate_provider_inputs(self.parser, options)

    @patch.dict(os.environ, {'INSIGHTS_ACCOUNT_ID': '12345', 'INSIGHTS_ORG_ID': '54321'})
    def test_ocp_inputs_insights_upload_account_org_ids(self):
        """
        Test where user passes an invalid ocp argument combination.
        """

        options = {'ocp': True, 'insights_upload': 'true', 'ocp_cluster_id': '123'}
        is_valid, _ = _validate_provider_inputs(self.parser, options)
        self.assertTrue(is_valid)

    @patch.dict(os.environ, {'INSIGHTS_USER': '12345', 'INSIGHTS_PASSWORD': '54321'})
    def test_ocp_inputs_insights_upload_user_pass(self):
        """
        Test where user passes an invalid ocp argument combination.
        """

        options = {'ocp': True, 'insights_upload': 'true', 'ocp_cluster_id': '123'}
        is_valid, _ = _validate_provider_inputs(self.parser, options)
        self.assertTrue(is_valid)

    def test_ocp_inputs_insights_upload_no_envs(self):
        """
        Test where user passes an invalid ocp argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'ocp': True, 'insights_upload': 'true', 'ocp_cluster_id': '123', 'upload_bool': True}
            _validate_provider_inputs(self.parser, options)

    def test_ocp_no_cluster_id(self):
        """
        Test where user passes ocp without cluster id combination.
        """
        with self.assertRaises(SystemExit):
            options = {'ocp': True}
            _validate_provider_inputs(self.parser, options)

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
        data = _load_yaml_file('tests/aws_static_report.yml')
        self.assertIsNotNone(data)

        data_missing = _load_yaml_file(None)
        self.assertIsNone(data_missing)

    def test_load_static_report_data(self):
        """
        Test to load static report data from option.
        """
        options = {}
        options['start_date'] = date.today()
        options['static_report_file'] = 'tests/aws_static_report.yml'
        _load_static_report_data(options)
        self.assertIsNotNone(options['static_report_data'])
        self.assertIsNotNone(options['start_date'])
        self.assertIsNotNone(options['end_date'])

        missing_options = {}
        _load_static_report_data(missing_options)
        self.assertIsNone(missing_options.get('static_report_data'))

    def test_load_static_report_data_no_start_date(self):
        """
        Test to load static report data from option with no start date.
        """
        options = {}
        options['static_report_file'] = 'tests/aws_static_report.yml'
        _load_static_report_data(options)
        self.assertIsNotNone(options.get('start_date'))
        self.assertIsNotNone(options.get('end_date'))

    def test_invalid_gcp_inputs(self):
        """
        Test where user args from azure, ocp, and aws when creating gcp data.
        """
        with self.assertRaises(SystemExit):
            options = {'gcp': True, 'azure_report_name': 'report'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'gcp': True, 'aws_bucket_name': 'mybucket'}
            _validate_provider_inputs(self.parser, options)
        with self.assertRaises(SystemExit):
            options = {'gcp': True, 'ocp_cluster_id': '123'}
            _validate_provider_inputs(self.parser, options)

    def test_invalid_gcp_inputs_aws_args(self):
        """
        Test where user aws arg when creating gcp data.
        """
        with self.assertRaises(SystemExit):
            options = {'gcp': True, 'aws_bucket_name': 'my-bucket'}
            _validate_provider_inputs(self.parser, options)

    def test_no_provider_type_fail(self):
        """
        Test that parser fails when no provider type is passed.
        """
        with self.assertRaises(SystemExit):
            options = {}
            _validate_provider_inputs(self.parser, options)
