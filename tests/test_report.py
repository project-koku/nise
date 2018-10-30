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
import csv
import datetime
import os
import shutil

from tempfile import (mkdtemp, NamedTemporaryFile)

from unittest import TestCase
from unittest.mock import ANY, patch

from nise.report import (aws_create_report,
                         ocp_create_report,
                         _create_month_list,
                         _write_csv,
                         _write_manifest)


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

    def test_aws_create_report_no_s3(self):
        """Test the aws report creation method no s3."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_report({'start_date': yesterday, 'end_date': now, 'aws_report_name': 'cur_report'})

        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    @patch('nise.upload.upload_to_s3')
    def test_aws_create_report_with_s3(self, mock_upload_to_s3):
        """Test the aws report creation method with s3."""
        mock_upload_to_s3.return_value = None
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {'start_date': yesterday,
                   'end_date': now,
                   'aws_bucket_name': 'my_bucket',
                   'aws_report_name': 'cur_report'}
        aws_create_report(options)
        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    def test_aws_create_report_with_local_dir(self):
        """Test the aws report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {'start_date': yesterday,
                   'end_date': now,
                   'aws_bucket_name': local_bucket_path,
                   'aws_report_name': 'cur_report'}
        aws_create_report(options)
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
            'end_date': datetime.datetime(year=2018, month=3, day=5),
            'expected_list': [{'name': 'January',
                               'start': datetime.datetime(year=2018, month=1, day=15),
                               'end': datetime.datetime(year=2018, month=1, day=31)},
                              {'name': 'February',
                               'start': datetime.datetime(year=2018, month=2, day=1),
                               'end': datetime.datetime(year=2018, month=2, day=28)},
                              {'name': 'March',
                               'start': datetime.datetime(year=2018, month=3, day=1),
                               'end': datetime.datetime(year=2018, month=3, day=5)}]},
                       ]

        for test_case in test_matrix:
            output = _create_month_list(test_case['start_date'], test_case['end_date'])
            self.assertCountEqual(output, test_case['expected_list'])

    def test_aws_create_report_with_local_dir_report_prefix(self):
        """Test the aws report creation method with local directory and a report prefix."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {'start_date': yesterday,
                   'end_date': now,
                   'aws_bucket_name': local_bucket_path,
                   'aws_report_name': 'cur_report',
                   'aws_prefix_name': 'my_prefix'}
        aws_create_report(options)
        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_bucket_path)

    def test_aws_create_report_finalize_report_copy(self):
        """Test that an aws finalized copy of a report file has an invoice id."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_report(
            {
                'start_date': yesterday,
                'end_date': now,
                'aws_report_name': 'cur_report',
                'aws_finalize_report': 'copy'
            }
        )

        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        finalized_file_name = '{}-finalized'.format(month_output_file_name)
        expected_month_output_file = '{}/{}.csv'.format(
            os.getcwd(),
            month_output_file_name
        )
        expected_finalized_file = '{}/{}.csv'.format(
            os.getcwd(),
            finalized_file_name
        )
        self.assertTrue(os.path.isfile(expected_month_output_file))
        self.assertTrue(os.path.isfile(expected_finalized_file))

        with open(expected_month_output_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertEqual(row['bill/InvoiceId'], '')

        with open(expected_finalized_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertNotEqual(row['bill/InvoiceId'], '')

        os.remove(expected_month_output_file)
        os.remove(expected_finalized_file)

    def test_aws_create_report_finalize_report_overwrite(self):
        """Test that an aws report file has an invoice id."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        aws_create_report(
            {
                'start_date': yesterday,
                'end_date': now,
                'aws_report_name': 'cur_report',
                'aws_finalize_report': 'overwrite'
            }
        )

        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   'cur_report')
        expected_month_output_file = '{}/{}.csv'.format(
            os.getcwd(),
            month_output_file_name
        )
        self.assertTrue(os.path.isfile(expected_month_output_file))

        with open(expected_month_output_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertNotEqual(row['bill/InvoiceId'], '')

        os.remove(expected_month_output_file)

    def test_ocp_create_report(self):
        """Test the ocp report creation method."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        cluster_id = '11112222'
        options = {'start_date': yesterday,
                   'end_date': now,
                   'ocp_cluster_id': cluster_id}
        ocp_create_report(options)
        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   cluster_id)
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)

    def test_ocp_create_report_with_local_dir(self):
        """Test the ocp report creation method with local directory."""
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_insights_upload = mkdtemp()
        cluster_id = '11112222'
        options = {'start_date': yesterday,
                   'end_date': now,
                   'insights_upload': local_insights_upload,
                   'ocp_cluster_id': cluster_id}
        ocp_create_report(options)
        month_output_file_name = '{}-{}-{}'.format(calendar.month_name[now.month],
                                                   now.year,
                                                   cluster_id)
        expected_month_output_file = '{}/{}.csv'.format(os.getcwd(), month_output_file_name)
        self.assertTrue(os.path.isfile(expected_month_output_file))
        os.remove(expected_month_output_file)
        shutil.rmtree(local_insights_upload)
