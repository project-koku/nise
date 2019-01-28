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
from datetime import datetime
from unittest import TestCase

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
        now = datetime.now()
        date_str = now.strftime('%m-%d-%Y')
        out_date = valid_date(date_str)
        self.assertEqual(now.date(), out_date.date())

    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

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

    def test_invalid_s3_inputs(self):
        """
        Test where user passes an invalid s3 argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'aws': True, 'aws_bucket_name': 'mybucket'}
            _validate_provider_inputs(self.parser, options)

    def test_invalid_ocp_inputs(self):
        """
        Test where user passes an invalid ocp argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'ocp': True, 'aws_bucket_name': 'mybucket', 'ocp_cluster_id': '123'}
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
        data = _load_yaml_file('tests/static_report.yml')
        self.assertIsNotNone(data)

        data_missing = _load_yaml_file(None)
        self.assertIsNone(data_missing)


    def test_load_static_report_data(self):
        """
        Test to load static report data from option.
        """
        options = {}
        options['start_date'] = datetime.today()
        options['static_report_file'] = 'tests/static_report.yml'
        _load_static_report_data(self.parser, options)
        self.assertIsNotNone(options['static_report_data'])
        self.assertIsNotNone(options['start_date'])

        missing_options = {}
        _load_static_report_data(self.parser, missing_options)
        self.assertIsNone(missing_options.get('static_report_data'))



    def test_load_static_report_data_no_start_date(self):
        """
        Test to load static report data from option with no start date.
        """
        options = {}
        options['static_report_file'] = 'tests/static_report.yml'
        with self.assertRaises(SystemExit):
            _load_static_report_data(self.parser, options)
