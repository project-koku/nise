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
import calendar
import datetime
import os
import shutil

from tempfile import (mkdtemp, NamedTemporaryFile)

from unittest import TestCase
from unittest.mock import ANY, patch

from moto import mock_s3

from nise.report import create_report, _create_month_list, _write_csv, _write_manifest


class ReportTestCase(TestCase):
    """
    TestCase class for report functions
    """

    def test_write_csv(self):
        """Test the writing of the CSV data."""
        temp_file = NamedTemporaryFile(mode='w', delete=False)
        headers = ['col1', 'col2']
        data = [{'col1': 'r1c1', 'col2': 'r1c2'},
                {'col1': 'r2c1', 'col2': 'r2c2'}]
        _write_csv(temp_file.name, data, headers)
        self.assertTrue(os.path.exists(temp_file.name))
        os.remove(temp_file.name)

    def test_write_manifest(self):
        """Test the writing of the manifest data."""
        data = '[{"col1": "r1c1", "col2": "r1c2"},' \
               '{"col1": "r2c1", "col2": "r2c2"}]'
        manifest_path = _write_manifest(data)
        self.assertTrue(os.path.exists(manifest_path))
        os.remove(manifest_path)

    def test_create_report_no_s3(self):
        """Test the report creation method no s3."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        create_report({'start_date': yesterday, 'end_date': now, 'report_name': 'cur_report'})

        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    @mock_s3
    def test_create_report_with_s3(self):
        """Test the report creation method with s3."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {'start_date': yesterday,
                   'end_date': now,
                   'bucket_name': 'my_bucket',
                   'report_name': 'cur_report'}
        create_report(options)
        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    def test_create_report_with_local_dir(self):
        """Test the report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {'start_date': yesterday,
                   'end_date': now,
                   'bucket_name': local_bucket_path,
                   'report_name': 'cur_report'}
        create_report(options)
        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_create_month_list(self):
        """Test to create month lists."""
        test_matrix = [{
                        'start_date': datetime.datetime(year=2018, month=1, day=15),
                        'end_date': datetime.datetime(year=2018, month=1, day=30),
                        'expected_list': [{'name': 'January',
                                           'start': datetime.datetime(year=2018, month=1, day=15),
                                           'end': datetime.datetime(year=2018, month=1, day=30)}]},
                        {
                        'start_date': datetime.datetime(year=2018, month=1, day=15),
                        'end_date': datetime.datetime(year=2018, month=3, day=30),
                        'expected_list': [{'name': 'January',
                                           'start': datetime.datetime(year=2018, month=1, day=15),
                                           'end': datetime.datetime(year=2018, month=1, day=31)},
                                           {'name': 'February',
                                           'start': datetime.datetime(year=2018, month=2, day=1),
                                           'end': datetime.datetime(year=2018, month=2, day=28)},
                                           {'name': 'March',
                                           'start': datetime.datetime(year=2018, month=3, day=1),
                                           'end': datetime.datetime(year=2018, month=3, day=31)}]},                    
                      ]
        
        for test_case in test_matrix:
            output = _create_month_list(test_case['start_date'], test_case['end_date'])
            self.assertCountEqual(output, test_case['expected_list'])
