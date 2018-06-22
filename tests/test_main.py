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
                           _check_s3_arguments,
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
            self.parser.parse_args(['--start-date', 'foo',
                                    '--output-file', 'out.csv'])

    def test_valid_s3_no_input(self):
        """
        Test where user passes no s3 argument combination.
        """
        options = {}
        valid = _check_s3_arguments(self.parser, options)
        self.assertTrue(valid)

    def test_valid_s3_both_inputs(self):
        """
        Test where user passes a valid s3 argument combination.
        """
        options = {'bucket_name': 'mybucket',
                    'report_name': 'cur'}
        valid = _check_s3_arguments(self.parser, options)
        self.assertTrue(valid)

    def test_invalid_s3_inputs(self):
        """
        Test where user passes an invalid s3 argument combination.
        """
        with self.assertRaises(SystemExit):
            options = {'bucket_name': 'mybucket'}
            _check_s3_arguments(self.parser, options)

    def test_main_no_inputs(self):
        """
        Test execution of main without inputs.
        """
        with self.assertRaises(SystemExit):
            main()
